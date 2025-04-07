import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List

class FmpAPI:    
    def __init__(self):
        """Initialize the API with credentials from environment variables."""
        load_dotenv()
        self.api_key = os.getenv("FMP_API_KEY")
        self.base_url = os.getenv("FMP_ENDPOINT")        
        if not self.api_key or not self.base_url:
            raise ValueError("Missing required environment variables for FMP API")
    
    def get_index_quotes(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get quotes for major market indices.
        
        Returns:
            List[Dict]: A list of dictionaries containing index data or None if the request fails
        """
        params = {
            "apikey": self.api_key
        }
        
        headers = {
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            return self._extract_index_data(data)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching index quotes: {e}")
            return None
    
    def _extract_index_data(self, data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Extract index data from the API response.
        
        Args:
            data: The JSON response from the API
            
        Returns:
            List[Dict]: A list of dictionaries containing index data or None if not found
        """
        try:
            # List of indices we're interested in
            target_symbols = ["^SPX", "^DJI", "^IXIC", "^RUT", "^NYA"]
            
            # Filter the data to only include our target symbols
            indices = [index for index in data if index.get("symbol") in target_symbols]
            
            # Extract the required fields for each index
            result = []
            for index in indices:
                index_data = {
                    "symbol": index.get("symbol"),
                    "price": index.get("price"),
                    "change": index.get("change"),
                    "volume": index.get("volume")
                }
                
                # Convert price and change to float if they exist
                if index_data["price"] is not None:
                    index_data["price"] = float(index_data["price"])
                
                if index_data["change"] is not None:
                    index_data["change"] = float(index_data["change"])
                
                # Convert volume to int if it exists
                if index_data["volume"] is not None:
                    index_data["volume"] = int(index_data["volume"])
                
                result.append(index_data)
            
            return result
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error parsing index data: {e}")
            return None
    
    def get_index_price(self, symbol: str) -> Optional[float]:
        """
        Get the current price of a specific index.
        
        Args:
            symbol: The symbol of the index (e.g., "^SPX")
            
        Returns:
            float: The current price of the index, or None if the request fails
        """
        indices = self.get_index_quotes()
        if not indices:
            return None
        
        for index in indices:
            if index["symbol"] == symbol:
                return index["price"]
        
        return None
