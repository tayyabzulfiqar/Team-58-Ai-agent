"""Firecrawl API Client - Production Ready"""
import os
import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class FirecrawlClient:
    """Production Firecrawl API client with retries and error handling"""
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key or os.getenv('FIRECRAWL_API_KEY', '')
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = "https://api.firecrawl.dev/v1"
        
        if not self.api_key:
            logger.warning("Firecrawl API key not provided")
    
    def scrape_url(self, url: str, selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scrape URL using Firecrawl API"""
        try:
            import requests
        except ImportError:
            logger.error("requests library not installed")
            return []
        
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
                    "formats": ["markdown"]
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
                    leads = self._parse_content(content, selectors, url)
                    logger.info(f"Extracted {len(leads)} leads from {url}")
                    return leads
                
                elif response.status_code == 429:
                    logger.warning("Rate limited, backing off...")
                    time.sleep(2 ** attempt)
                    continue
                
                elif response.status_code == 401:
                    logger.error("Invalid API key")
                    return []
                
                else:
                    logger.error(f"API error {response.status_code}: {response.text[:200]}")
                    if attempt == self.max_retries - 1:
                        return []
                    time.sleep(2 ** attempt)
                    
            except requests.exceptions.Timeout:
                logger.error(f"Timeout scraping {url}")
                if attempt == self.max_retries - 1:
                    return []
                time.sleep(2 ** attempt)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {str(e)}")
                if attempt == self.max_retries - 1:
                    return []
                time.sleep(2 ** attempt)
                
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                if attempt == self.max_retries - 1:
                    return []
                time.sleep(2 ** attempt)
        
        return []
    
    def _parse_content(self, content: str, selectors: Dict[str, str], url: str) -> List[Dict[str, Any]]:
        """Parse scraped content into structured leads"""
        leads = []
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
            
            if '@' in line and '.' in line and ' ' not in line:
                current_lead['email'] = line
            elif line.startswith('# ') or line.startswith('## '):
                current_lead['name'] = line.replace('#', '').strip()
            elif len(line) > 20 and not line.startswith('!'):
                current_lead['description'] = line[:200]
        
        if current_lead:
            current_lead['source_url'] = url
            leads.append(current_lead)
        
        return leads if leads else [{"source_url": url, "content": content[:500]}]
