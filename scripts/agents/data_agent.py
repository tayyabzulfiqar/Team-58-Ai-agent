"""
Real Data Engine - Production-Ready Data Ingestion Layer
Multi-source data fetching with retries, validation, and error handling
"""

import os

# Load environment variables from .env file (for local development)
# In Railway, env vars are already set in the environment
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("SUCCESS: Loaded environment from .env file")
except ImportError:
    print("INFO: python-dotenv not installed, using system environment variables")

import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Firecrawl API Key Detection
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
if not FIRECRAWL_API_KEY:
    print("WARNING: Firecrawl API key NOT found")
    logger.warning("Firecrawl API key not found in environment variables")
    logger.info("Please set FIRECRAWL_API_KEY in your .env file or Railway environment")
else:
    print("SUCCESS: Firecrawl API key loaded")
    logger.info(f"Firecrawl API key found (length: {len(FIRECRAWL_API_KEY)} chars)")


class FirecrawlClient:
    """Production Firecrawl API client with retries and error handling"""
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key or os.getenv('FIRECRAWL_API_KEY')
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = "https://api.firecrawl.dev/v1"
        
        if not self.api_key:
            logger.warning("Firecrawl API key not provided")
    
    def scrape_url(self, url: str, selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Scrape URL using Firecrawl API
        
        Args:
            url: URL to scrape
            selectors: CSS selectors for data extraction
            
        Returns:
            List of extracted data dictionaries
        """
        import requests
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Firecrawl scraping {url} (attempt {attempt + 1}/{self.max_retries})")
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "url": url,
                    "onlyMainContent": False,
                    "formats": ["markdown"],
                    "includeTags": list(selectors.values()) if selectors else []
                }
                
                response = requests.post(
                    f"{self.base_url}/scrape",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get('data', {}).get('markdown', '')
                    
                    # Parse content based on selectors
                    leads = self._parse_content(content, selectors, url)
                    logger.info(f"Successfully extracted {len(leads)} leads from {url}")
                    return leads
                
                elif response.status_code == 429:
                    logger.warning(f"Rate limited, waiting...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                else:
                    logger.error(f"Firecrawl API error: {response.status_code} - {response.text}")
                    if attempt == self.max_retries - 1:
                        return []
                    time.sleep(2 ** attempt)
                    
            except requests.exceptions.Timeout:
                logger.error(f"Timeout scraping {url}")
                if attempt == self.max_retries - 1:
                    return []
                time.sleep(2 ** attempt)
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                if attempt == self.max_retries - 1:
                    return []
                time.sleep(2 ** attempt)
        
        return []
    
    def _parse_content(self, content: str, selectors: Dict[str, str], url: str) -> List[Dict[str, Any]]:
        """Parse scraped content into structured leads"""
        leads = []
        
        # Simple parsing - in production, use proper HTML parsing
        lines = content.split('\n')
        current_lead = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_lead:
                    current_lead['source_url'] = url
                    leads.append(current_lead)
                    current_lead = {}
                continue
            
            # Extract based on patterns
            if '@' in line and '.' in line:
                current_lead['email'] = line
            elif line.startswith('# ') or line.startswith('## '):
                current_lead['name'] = line.replace('#', '').strip()
            elif len(line) > 20:
                current_lead['description'] = line[:200]
        
        if current_lead:
            current_lead['source_url'] = url
            leads.append(current_lead)
        
        return leads if leads else [{"source_url": url, "content": content[:500]}]


class RedditClient:
    """Production Reddit API client with retries and error handling"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None,
                 user_agent: str = "DataAgent/1.0", timeout: int = 30, max_retries: int = 3):
        self.client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries
        self.access_token = None
        
        if self.client_id and self.client_secret:
            self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Reddit API"""
        import requests
        
        try:
            auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
            
            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth,
                data={
                    'grant_type': 'client_credentials'
                },
                headers={'User-Agent': self.user_agent},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.access_token = response.json().get('access_token')
                logger.info("Reddit authentication successful")
            else:
                logger.error(f"Reddit auth failed: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Reddit authentication error: {str(e)}")
    
    def search_subreddit(self, subreddit: str, keywords: List[str], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search subreddit for posts matching keywords
        
        Args:
            subreddit: Subreddit name
            keywords: List of keywords to search for
            limit: Maximum posts to return
            
        Returns:
            List of post dictionaries
        """
        import requests
        
        if not self.access_token:
            logger.error("Reddit not authenticated")
            return []
        
        all_posts = []
        
        for keyword in keywords:
            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Searching r/{subreddit} for '{keyword}'")
                    
                    headers = {
                        'Authorization': f'Bearer {self.access_token}',
                        'User-Agent': self.user_agent
                    }
                    
                    params = {
                        'q': keyword,
                        'limit': min(limit, 25),  # Reddit limit per request
                        'sort': 'new',
                        't': 'week'  # Last week
                    }
                    
                    response = requests.get(
                        f'https://oauth.reddit.com/r/{subreddit}/search',
                        headers=headers,
                        params=params,
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts:
                            post_data = post.get('data', {})
                            all_posts.append({
                                'id': post_data.get('id'),
                                'title': post_data.get('title', ''),
                                'selftext': post_data.get('selftext', ''),
                                'author': post_data.get('author', ''),
                                'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                'created_utc': post_data.get('created_utc'),
                                'score': post_data.get('score', 0),
                                'num_comments': post_data.get('num_comments', 0),
                                'subreddit': subreddit,
                                'matched_keyword': keyword
                            })
                        
                        break  # Success, move to next keyword
                    
                    elif response.status_code == 429:
                        logger.warning("Reddit rate limited, backing off...")
                        time.sleep(2 ** attempt)
                    
                    else:
                        logger.error(f"Reddit API error: {response.status_code}")
                        time.sleep(2 ** attempt)
                
                except requests.exceptions.Timeout:
                    logger.error(f"Reddit timeout for r/{subreddit}")
                    time.sleep(2 ** attempt)
                
                except Exception as e:
                    logger.error(f"Reddit error: {str(e)}")
                    time.sleep(2 ** attempt)
        
        # Remove duplicates by ID
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post['id'] not in seen_ids:
                seen_ids.add(post['id'])
                unique_posts.append(post)
        
        logger.info(f"Found {len(unique_posts)} unique posts from r/{subreddit}")
        return unique_posts[:limit]


class DataValidator:
    """Production data validation layer"""
    
    REQUIRED_FIELDS = ['id', 'source']
    
    def validate(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a data record
        
        Returns:
            Dict with 'valid' (bool), 'score' (float), and 'errors' (list)
        """
        errors = []
        score = 1.0
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in record or not record[field]:
                errors.append(f"Missing required field: {field}")
                score -= 0.3
        
        # Check for meaningful content
        content_fields = ['name', 'title', 'content', 'description', 'email']
        has_content = any(record.get(f) for f in content_fields)
        if not has_content:
            errors.append("No meaningful content found")
            score -= 0.5
        
        # Validate email if present
        if 'email' in record and record['email']:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(record['email'])):
                errors.append("Invalid email format")
                score -= 0.2
        
        score = max(0.0, score)
        
        return {
            'valid': score > 0.5 and len(errors) == 0,
            'score': round(score, 2),
            'errors': errors
        }
    
    def clean(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize a record"""
        cleaned = record.copy()
        
        # Truncate long text fields
        text_fields = ['content', 'description', 'selftext']
        for field in text_fields:
            if field in cleaned and cleaned[field]:
                cleaned[field] = str(cleaned[field])[:1000]
        
        # Normalize strings
        if 'name' in cleaned and cleaned['name']:
            cleaned['name'] = str(cleaned['name']).strip()[:100]
        
        # Add processing metadata
        cleaned['_processed_at'] = datetime.now().isoformat()
        cleaned['_processed_version'] = '1.0'
        
        return cleaned


class DataAgent:
    """
    Production data ingestion agent
    Fetches real data from multiple sources with full error handling
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        
        # Initialize source clients
        self.firecrawl_client = FirecrawlClient()
        self.reddit_client = RedditClient()
        self.validator = DataValidator()
        
        self.metadata = {
            "session_id": self.session_id,
            "start_time": None,
            "end_time": None,
            "sources": {},
            "total_records": 0,
            "valid_records": 0,
            "invalid_records": 0
        }
        
        logger.info(f"DataAgent initialized with session_id: {self.session_id}")
    
    def collect_data(self, sources_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main data collection method
        
        Args:
            sources_config: Dict with source configurations
            Example:
            {
                "firecrawl": {
                    "urls": ["https://example.com/leads"],
                    "selectors": {"name": "h2", "email": "a[href^='mailto:']"}
                },
                "reddit": {
                    "subreddits": ["startups"],
                    "keywords": ["looking for"],
                    "limit": 50
                }
            }
        
        Returns:
            Dict with collected data, validation results, and metadata
        """
        self.metadata["start_time"] = datetime.now().isoformat()
        start_time = time.time()
        
        all_raw_data = []
        errors = []
        
        try:
            # Collect from each source
            if "firecrawl" in sources_config:
                try:
                    firecrawl_data = self._fetch_from_firecrawl(sources_config["firecrawl"])
                    all_raw_data.extend(firecrawl_data)
                    self.metadata["sources"]["firecrawl"] = {
                        "status": "success",
                        "records": len(firecrawl_data)
                    }
                except Exception as e:
                    error_msg = f"Firecrawl error: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    self.metadata["sources"]["firecrawl"] = {"status": "error", "error": str(e)}
            
            if "reddit" in sources_config:
                try:
                    reddit_data = self._fetch_from_reddit(sources_config["reddit"])
                    all_raw_data.extend(reddit_data)
                    self.metadata["sources"]["reddit"] = {
                        "status": "success",
                        "records": len(reddit_data)
                    }
                except Exception as e:
                    error_msg = f"Reddit error: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    self.metadata["sources"]["reddit"] = {"status": "error", "error": str(e)}
            
            # Validate and process all collected data
            processed_data = self._process_collected_data(all_raw_data)
            
            # Calculate metadata
            end_time = time.time()
            self.metadata["end_time"] = datetime.now().isoformat()
            self.metadata["duration_seconds"] = round(end_time - start_time, 2)
            self.metadata["total_records"] = len(all_raw_data)
            self.metadata["valid_records"] = len(processed_data)
            self.metadata["invalid_records"] = len(all_raw_data) - len(processed_data)
            
            result = {
                "session_id": self.session_id,
                "success": len(processed_data) > 0,
                "data": processed_data,
                "metadata": self.metadata,
                "errors": errors if errors else None,
                "stats": {
                    "total_fetched": len(all_raw_data),
                    "valid": len(processed_data),
                    "invalid": len(all_raw_data) - len(processed_data),
                    "sources_attempted": len(sources_config),
                    "sources_successful": len([s for s in self.metadata["sources"].values() if s.get("status") == "success"])
                }
            }
            
            logger.info(f"Data collection complete: {len(processed_data)} valid records")
            
            return result
            
        except Exception as e:
            logger.error(f"Critical error in data collection: {str(e)}")
            return {
                "session_id": self.session_id,
                "success": False,
                "data": [],
                "metadata": self.metadata,
                "errors": errors + [str(e)],
                "stats": {
                    "total_fetched": 0,
                    "valid": 0,
                    "invalid": 0,
                    "sources_attempted": len(sources_config),
                    "sources_successful": 0
                }
            }
    
    def _fetch_from_firecrawl(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch data from Firecrawl"""
        urls = config.get("urls", [])
        selectors = config.get("selectors", {})
        
        if not urls:
            logger.warning("No URLs provided for Firecrawl")
            return []
        
        all_leads = []
        for url in urls:
            leads = self.firecrawl_client.scrape_url(url, selectors)
            for lead in leads:
                lead["_source"] = "firecrawl"
                lead["_source_url"] = url
                lead["_fetched_at"] = datetime.now().isoformat()
                lead["id"] = lead.get("id") or f"firecrawl_{uuid.uuid4().hex[:8]}"
            all_leads.extend(leads)
        
        return all_leads
    
    def _fetch_from_reddit(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch data from Reddit"""
        subreddits = config.get("subreddits", [])
        keywords = config.get("keywords", [])
        limit = config.get("limit", 50)
        
        if not subreddits:
            logger.warning("No subreddits provided for Reddit")
            return []
        
        all_leads = []
        for subreddit in subreddits:
            posts = self.reddit_client.search_subreddit(subreddit, keywords, limit)
            for post in posts:
                lead = self._reddit_post_to_lead(post, subreddit)
                all_leads.append(lead)
        
        return all_leads
    
    def _reddit_post_to_lead(self, post: Dict[str, Any], subreddit: str) -> Dict[str, Any]:
        """Convert Reddit post to standardized lead format"""
        return {
            "id": f"reddit_{post.get('id', 'unknown')}",
            "name": post.get('author', 'unknown'),
            "title": post.get('title', ''),
            "content": post.get('selftext', '')[:500],
            "source": "reddit",
            "subreddit": subreddit,
            "url": post.get('url', ''),
            "created_utc": post.get('created_utc'),
            "score": post.get('score', 0),
            "num_comments": post.get('num_comments', 0),
            "matched_keyword": post.get('matched_keyword', ''),
            "_source": "reddit",
            "_source_subreddit": subreddit,
            "_fetched_at": datetime.now().isoformat()
        }
    
    def _process_collected_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and validate all collected data"""
        logger.info(f"Processing {len(raw_data)} raw records")
        
        validated_data = []
        
        for idx, record in enumerate(raw_data):
            try:
                validation_result = self.validator.validate(record)
                
                if validation_result["valid"]:
                    cleaned_record = self.validator.clean(record)
                    cleaned_record["_validation_score"] = validation_result["score"]
                    validated_data.append(cleaned_record)
                else:
                    logger.debug(f"Record {idx} failed validation: {validation_result['errors']}")
                    
            except Exception as e:
                logger.error(f"Error processing record {idx}: {str(e)}")
                continue
        
        # Remove duplicates
        seen_ids = set()
        unique_data = []
        for record in validated_data:
            record_id = record.get("id", str(uuid.uuid4()))
            if record_id not in seen_ids:
                seen_ids.add(record_id)
                unique_data.append(record)
        
        logger.info(f"Processed {len(raw_data)} records: {len(unique_data)} valid unique records")
        
        return unique_data
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return {
            "session_id": self.session_id,
            "metadata": self.metadata,
            "errors_count": len(self.errors) if hasattr(self, 'errors') else 0,
            "sources_attempted": list(self.metadata["sources"].keys()),
            "collection_complete": self.metadata.get("end_time") is not None
        }


# Backward compatibility - keep old interface
class LegacyDataAgent:
    """Legacy interface for backward compatibility"""
    
    def __init__(self):
        self.agent = DataAgent()
    
    def collect_raw_data(self):
        """Legacy method - redirects to new implementation with demo config"""
        # Demo config for backward compatibility
        demo_config = {
            "reddit": {
                "subreddits": ["startups"],
                "keywords": ["looking for"],
                "limit": 5
            }
        }
        result = self.agent.collect_data(demo_config)
        return result.get("data", [])


if __name__ == "__main__":
    print("=" * 60)
    print("REAL DATA ENGINE - PRODUCTION MODE")
    print("=" * 60)
    
    # Check environment
    firecrawl_key = os.getenv('FIRECRAWL_API_KEY')
    reddit_id = os.getenv('REDDIT_CLIENT_ID')
    
    print(f"\nEnvironment Check:")
    print(f"  Firecrawl API Key: {'✓ Set' if firecrawl_key else '✗ Not Set'}")
    print(f"  Reddit Client ID: {'✓ Set' if reddit_id else '✗ Not Set'}")
    
    # Initialize agent
    agent = DataAgent()
    
    # Configure sources
    config = {
        "reddit": {
            "subreddits": ["startups", "entrepreneur"],
            "keywords": ["looking for", "need help", "recommendation"],
            "limit": 10
        }
    }
    
    if firecrawl_key:
        config["firecrawl"] = {
            "urls": ["https://example.com"],
            "selectors": {"title": "h1"}
        }
    
    # Collect data
    print(f"\n{'='*60}")
    print("STARTING DATA COLLECTION...")
    print(f"{'='*60}\n")
    
    result = agent.collect_data(config)
    
    # Print results
    print(f"\n{'='*60}")
    print("COLLECTION RESULTS")
    print(f"{'='*60}")
    print(f"Session ID: {result['session_id']}")
    print(f"Success: {result['success']}")
    print(f"Duration: {result['metadata'].get('duration_seconds', 'N/A')} seconds")
    print(f"Valid Records: {result['stats']['valid']}")
    print(f"Invalid Records: {result['stats']['invalid']}")
    print(f"Sources Successful: {result['stats']['sources_successful']}/{result['stats']['sources_attempted']}")
    
    if result['errors']:
        print(f"\nErrors ({len(result['errors'])}):")
        for error in result['errors']:
            print(f"  - {error}")
    
    # Show sample data
    if result['data']:
        print(f"\n{'='*60}")
        print("SAMPLE RECORD")
        print(f"{'='*60}")
        print(json.dumps(result['data'][0], indent=2, default=str))
    
    print(f"\n{'='*60}")
    print("DATA COLLECTION COMPLETE")
    print(f"{'='*60}")
