import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

class CoinMarketCapAPI:    
    def __init__(self):
        """Initialize the API with credentials from environment variables."""
        load_dotenv()
        self.api_key = os.getenv("COINMARKETCAP_API_KEY")
        self.base_url = os.getenv("COINMARKETCAP_ENDPOINT")
        
        if not self.api_key or not self.base_url:
            raise ValueError("Missing required environment variables for CoinMarketCap API")
    
    def get_bitcoin_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the current Bitcoin data including price and other metrics.
        
        Returns:
            Dict: A dictionary containing Bitcoin data or None if the request fails
        """
        params = {
            "slug": "bitcoin",
            "convert": "USD"
        }
        
        headers = {
            "X-CMC_PRO_API_KEY": self.api_key,
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
            return self._extract_bitcoin_data(data)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Bitcoin data: {e}")
            return None
    
    def _extract_bitcoin_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract Bitcoin data from the API response.
        
        Args:
            data: The JSON response from the API
            
        Returns:
            Dict: A dictionary containing Bitcoin data or None if not found
        """
        try:
            # Navigate the nested JSON structure to get the data
            bitcoin_data = data.get("data", {}).get("1", {})
            quote = bitcoin_data.get("quote", {})
            usd_data = quote.get("USD", {})
            
            # Extract the required fields
            result = {
                "price": usd_data.get("price"),
                "percent_change_1h": usd_data.get("percent_change_1h"),
                "percent_change_24h": usd_data.get("percent_change_24h"),
                "last_updated": usd_data.get("last_updated")
            }
            
            # Convert price to float if it exists
            if result["price"] is not None:
                result["price"] = float(result["price"])
            
            # Convert percent changes to float if they exist
            for field in ["percent_change_1h", "percent_change_24h"]:
                if result[field] is not None:
                    result[field] = float(result[field])
            
            # Convert last_updated to datetime if it exists
            if result["last_updated"] is not None:
                result["last_updated"] = datetime.fromisoformat(result["last_updated"].replace("Z", "+00:00"))
            
            return result
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error parsing Bitcoin data: {e}")
            return None
    
    def get_bitcoin_price(self) -> Optional[float]:
        """
        Get the current price of Bitcoin in USD.
        
        Returns:
            float: The current price of Bitcoin in USD, or None if the request fails
        """
        data = self.get_bitcoin_data()
        return data["price"] if data else None
