"""Reddit API Client - Production Ready"""
import os
import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class RedditClient:
    """Production Reddit API client with retries and error handling"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None,
                 user_agent: str = "DataAgent/1.0", timeout: int = 30, max_retries: int = 3):
        self.client_id = client_id or os.getenv('REDDIT_CLIENT_ID', '')
        self.client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET', '')
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries
        self.access_token = None
        
        if self.client_id and self.client_secret:
            self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Reddit API"""
        try:
            import requests
        except ImportError:
            logger.error("requests library not installed")
            return
        
        try:
            auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
            
            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth,
                data={'grant_type': 'client_credentials'},
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
        """Search subreddit for posts matching keywords"""
        try:
            import requests
        except ImportError:
            logger.error("requests library not installed")
            return []
        
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
                        'limit': min(limit, 25),
                        'sort': 'new',
                        't': 'week'
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
                        
                        break
                    
                    elif response.status_code == 429:
                        logger.warning("Reddit rate limited")
                        time.sleep(2 ** attempt)
                    
                    elif response.status_code == 401:
                        logger.error("Reddit auth expired")
                        return []
                    
                    else:
                        logger.error(f"Reddit API error: {response.status_code}")
                        time.sleep(2 ** attempt)
                
                except Exception as e:
                    logger.error(f"Reddit error: {str(e)}")
                    time.sleep(2 ** attempt)
        
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post['id'] not in seen_ids:
                seen_ids.add(post['id'])
                unique_posts.append(post)
        
        logger.info(f"Found {len(unique_posts)} unique posts from r/{subreddit}")
        return unique_posts[:limit]
