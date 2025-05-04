from src.scraper import BaseScraper



class WeatherGrabber24(BaseScraper):
    def __init__(self, requester=None, requester_config=None, parser=None, parser_type="html.parser"):
        parser_type = "json"
        if not requester_config:
            requester_config = {}
            requester_config["respect_robots_txt"] = False # API doesn't require robotx.txt checking
        
        super().__init__(requester, requester_config, parser, parser_type)
        
    
    def extract_data(self, parsed_content) -> dict:
        res = {}
        data = parsed_content["items"]
        records = data[0]
        timestamp = records["update_timestamp"]
        
        res["timestamp"] = timestamp
        res["validity"] = records["valid_period"]
        #Get general weather forecast
        res["general"] = records["general"]
        #Get weather forecast for zones
        regional_data = records["periods"][0]["regions"]
        res["west"] = regional_data["west"]
        res["central"] = regional_data["central"]
        res["east"] = regional_data["east"]
        res["south"] = regional_data["south"]
        res["north"] = regional_data["north"]
        
        return res
        
class WeatherGrabber2(BaseScraper):
    def __init__(self, requester=None, requester_config=None, parser=None, parser_type="html.parser"):
        parser_type = "json"
        if not requester_config:
            requester_config = {}
            requester_config["respect_robots_txt"] = False # API doesn't require robotx.txt checking
        
        super().__init__(requester, requester_config, parser, parser_type)
        
    
    def extract_data(self, parsed_content) -> dict:
        res = {}
        data = parsed_content["data"]
        
        records = data["records"][0]
        
        timestamp = records["timestamp"]
        
        res["timestamp"] = timestamp
        
        res["general"] = records["general"]
        res["forecast"] = records["forecast"]
        res["validPeriod"] = records["validPeriod"]
        
        return res
    
class RHGrabber(BaseScraper):
    def __init__(self, requester=None, requester_config=None, parser=None, parser_type="html.parser"):
        parser_type = "json"
        if not requester_config:
            requester_config = {}
            requester_config["respect_robots_txt"] = False # API doesn't require robotx.txt checking
        
        super().__init__(requester, requester_config, parser, parser_type)
        
    def extract_data(self, parsed_content):
        res = {}
        stations = parsed_content.get("data").get("stations",{})
        readings = parsed_content.get("data").get("readings",{})
        res["stations"] = stations
        res["readings"] = readings
        return res

class AirTempGrabber(BaseScraper):
    def __init__(self, requester=None, requester_config=None, parser=None, parser_type="html.parser"):
        parser_type = "json"
        if not requester_config:
            requester_config = {}
            requester_config["respect_robots_txt"] = False # API doesn't require robotx.txt checking
        
        super().__init__(requester, requester_config, parser, parser_type)
    
    def extract_data(self, parsed_content):
        return super().extract_data(parsed_content)
    def extract_data(self, parsed_content):
        res = {}
        stations = parsed_content.get("data").get("stations",{})
        readings = parsed_content.get("data").get("readings",{})
        res["stations"] = stations
        res["readings"] = readings
        return res
