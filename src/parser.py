from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import json


class BaseParser(ABC):
    """Base class for all parsers"""
    
    @abstractmethod
    def parse(self, content):
        """Parse the content and extract data.
        
        Args:
            content (str): The content to parse
            
        Returns:
            dict: Extracted data
        """
        pass


class HTMLParser(BaseParser):
    """Parser for HTML content using BeautifulSoup"""
    
    def __init__(self, parser_type="html.parser"):
        """Initialize the HTML parser.
        
        Args:
            parser_type (str): BeautifulSoup parser type (html.parser, lxml, etc.)
        """
        self.parser_type = parser_type
    
    def parse(self, content):
        """Parse HTML content using BeautifulSoup.
        
        Args:
            content (str): HTML content
            
        Returns:
            BeautifulSoup: Parsed HTML content
        """
        return BeautifulSoup(content, self.parser_type)
    
    def extract_text(self, content, selector):
        """Extract text from elements matching the CSS selector.
        
        Args:
            content (str): HTML content
            selector (str): CSS selector
            
        Returns:
            list: List of extracted text
        """
        soup = self.parse(content)
        elements = soup.select(selector)
        return [element.text.strip() for element in elements]
    
    def extract_attribute(self, content, selector, attribute):
        """Extract attribute from elements matching the CSS selector.
        
        Args:
            content (str): HTML content
            selector (str): CSS selector
            attribute (str): Attribute name
            
        Returns:
            list: List of extracted attribute values
        """
        soup = self.parse(content)
        elements = soup.select(selector)
        return [element.get(attribute) for element in elements if element.has_attr(attribute)]


class JSONParser(BaseParser):
    """Parser for JSON content"""
    
    def parse(self, content):
        """Parse JSON content.
        
        Args:
            content (str): JSON content
            
        Returns:
            dict: Parsed JSON content
        """
        return json.loads(content)
    
    def extract_value(self, content, path):
        """Extract value using JSON path.
        
        Args:
            content (str): JSON content
            path (list): List of keys representing the path
            
        Returns:
            Any: Extracted value
        """
        data = self.parse(content) if isinstance(content, str) else content
        
        for key in path:
            if isinstance(data, dict) and key in data:
                data = data[key]
            elif isinstance(data, list) and isinstance(key, int) and key < len(data):
                data = data[key]
            else:
                return None
        
        return data


class XMLParser(BaseParser):
    """Parser for XML content"""
    
    def __init__(self):
        """Initialize the XML parser."""
        try:
            import xml.etree.ElementTree as ET
            self.ET = ET
        except ImportError:
            raise ImportError("xml.etree.ElementTree is required for XMLParser")
    
    def parse(self, content):
        """Parse XML content.
        
        Args:
            content (str): XML content
            
        Returns:
            ElementTree: Parsed XML content
        """
        return self.ET.fromstring(content)
    
    def extract_text(self, content, xpath):
        """Extract text using XPath.
        
        Args:
            content (str): XML content
            xpath (str): XPath expression
            
        Returns:
            list: List of extracted text
        """
        root = self.parse(content) if isinstance(content, str) else content
        elements = root.findall(xpath)
        return [element.text.strip() if element.text else "" for element in elements]


# Factory to create parser based on content type
def create_parser(content_type):
    """Factory function to create appropriate parser based on content type.
    
    Args:
        content_type (str): Content type (html, json, xml)
        
    Returns:
        BaseParser: Parser instance
    """
    content_type = content_type.lower()
    
    if content_type in ['html', 'html.parser', 'lxml', 'html5lib']:
        return HTMLParser(parser_type=content_type)
    elif content_type == 'json':
        return JSONParser()
    elif content_type == 'xml':
        return XMLParser()
    else:
        raise ValueError(f"Unsupported content type: {content_type}")