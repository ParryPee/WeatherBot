import requests
import logging
import time
from abc import abstractmethod
import random
from urllib.robotparser import RobotFileParser
from requests.exceptions import RequestException
import json


class Requester:
    """Handles all HTTP operations and fetches the requested pages, has parameters for rate limits robotx.txt etc."""
    def __init__(self,
        headers=None,
        cookies=None,
        timeout=30,
        retry_count=3,
        retry_delay=2,
        verify_ssl=True,
        user_agent_rotation = False,
        rate_limit=0,
        respect_robots_txt=True):


        #Request variables
        self.headers = headers or {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'} #set headers to the given parameters or use a standard user-agent
        self.cookies = cookies or {} #If no cookie specified set it to None
        self.timeout = timeout #Default is 30
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
        self.user_agent_rotation = user_agent_rotation
        self.rate_limit = rate_limit
        self.respect_robots_txt = respect_robots_txt
        self.last_request_time = 0
        
        # Collection of user agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        ]
        #initialise session for http requests
        self.session = requests.session()

        self.session.headers.update(self.headers)
        self.session.cookies.update(self.cookies)


        self.robots_cache = {}

        self.logger = logging.getLogger(__name__)

    def _rotate_user_agent(self):
        """selects a random user agent"""
        if self.user_agent_rotation:
            self.session.headers['User-Agent'] = random.choice(self.user_agents)

    
    def _respect_rate_limit(self):
        """Rate limit between requests"""
        if self.rate_limit > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit:
                time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()

    def _check_robots_txt(self,url):
        """Check if scraping is allowed by robots.txt."""
        if not self.respect_robots_txt:
            return True
        
        from urllib.parse import urlparse

        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = base_url+"/robots.txt"

        if base_url not in self.robots_cache:
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
                self.robots_cache[base_url] = rp
            except Exception as e:
                self.logger.warning(f"Failed to read robots.txt at {robots_url}: {e}")
                return True
        
        user_agent = self.session.headers.get('User-Agent','*')
        return self.robots_cache[base_url].can_fetch(user_agent,url)
    
    def get(self,url,params = None, **kwargs):
        """        Make a GET request with retry logic and optional rate limiting.
        
        Args:
            url (str): URL to fetch
            params (dict, optional): Query parameters
            **kwargs: Additional arguments to pass to requests.get
            
        Returns:
            Response: The HTTP response object
            
        Raises:
            RequestException: If the request fails after all retries"""

        if not self._check_robots_txt(url):
            self.logger.warning(f"ROBOTS.TXT DOES NOT ALLOW SCRAPING FOR {url}")
            raise PermissionError(f"Robots.txt disallows scraping")
        
        merged_kwargs = {
            'timeout': self.timeout,
            'verify': self.verify_ssl


        }
        merged_kwargs.update(kwargs)
        for attempt in range(self.retry_count + 1):
            try:
                self._rotate_user_agent()
                self._respect_rate_limit()

                self.logger.debug(f"Requesting url {url}")
                resp = self.session.get(url,params=params,**merged_kwargs)
                resp.raise_for_status()
                return resp
            except RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt+1}/{self.retry_count+1}): {str(e)}")
                
                if attempt < self.retry_count:
                    # Exponential backoff
                    sleep_time = self.retry_delay * (2 ** attempt)
                    self.logger.info(f"Retrying in {sleep_time} seconds")
                    time.sleep(sleep_time)
                else:
                    self.logger.error(f"Request failed after {self.retry_count+1} attempts")
                    raise
    
    def post(self,url,body = None,**kwargs):
        if not self._check_robots_txt(url):
            self.logger.warning(f"ROBOTS.TXT DOES NOT ALLOW SCRAPING FOR {url}")
            raise PermissionError(f"Robots.txt disallows scraping")
        merged_kwargs = {
            'timeout': self.timeout,
            'verify': self.verify_ssl


        }
        merged_kwargs.update(kwargs)
        for attempt in range(self.retry_count + 1):
            try:
                self._rotate_user_agent()
                self._respect_rate_limit()
                
                resp = self.session.post(url, json=body)
                resp.raise_for_status()
                
                return resp
            except RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt+1}/{self.retry_count+1}): {str(e)}")
                
                if attempt < self.retry_count:
                    # Exponential backoff
                    sleep_time = self.retry_delay * (2 ** attempt)
                    self.logger.info(f"Retrying in {sleep_time} seconds")
                    time.sleep(sleep_time)
                else:
                    self.logger.error(f"Request failed after {self.retry_count+1} attempts")
                    raise
                








