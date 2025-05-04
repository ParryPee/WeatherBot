from abc import ABC, abstractmethod
from src.requester import Requester
from src.parser import create_parser


class BaseScraper(ABC):
    def __init__(self,
                 requester=None,
                 requester_config=None,
                 parser=None,
                 parser_type="html.parser"):
        
        # Either use provided requester or create a new one with optional config
        self.requester = requester or Requester(**(requester_config or {}))
        
        # Either use provided parser or create one based on parser_type
        self.parser = parser or create_parser(parser_type)
        self.parser_type = parser_type

    @abstractmethod
    def extract_data(self, parsed_content):
        """Extract specific data from the parsed content.
        
        Args:
            parsed_content: Content that has been parsed by the parser
            
        Returns:
            dict: Extracted data
        """
        return parsed_content
    
    def fetch(self, url, params=None, protocol="GET", **kwargs):
        """Fetch content from the given URL using the requester.
        
        Args:
            url (str): URL to fetch
            params (dict, optional): Query parameters
            **kwargs: Additional arguments to pass to requester
            
        Returns:
            str: Raw content
        """
        if protocol == "GET":
            response = self.requester.get(url, params=params, **kwargs)
            return response.text
        elif protocol == "POST":
            json_body = kwargs["body"]
            response = self.requester.post(url,json_body)
            return response.text
    
    def parse(self, content):
        """Parse the content using the parser.
        
        Args:
            content (str): Content to parse
            
        Returns:
            Any: Parsed content
        """
        return self.parser.parse(content)
    
    def scrape(self, url, params=None,protocol = "GET", **kwargs):
        """Main method to perform scraping operation.
        
        Args:
            url (str): URL to scrape
            params (dict, optional): Query parameters
            **kwargs: Additional arguments to pass to requester
            
        Returns:
            dict: Extracted data
        """
        if protocol == "GET":
            content = self.fetch(url, params, **kwargs)
            parsed_content = self.parse(content)
            return self.extract_data(parsed_content)
        elif protocol == "POST":
            body = kwargs["body"]
            content = self.fetch(url,params,protocol,body=body)
            parsed_content = self.parse(content)
            return self.extract_data(parsed_content)
        
        
