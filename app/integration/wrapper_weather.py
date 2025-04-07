import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from datetime import datetime

class WeatherAPI:    
    def __init__(self):
        """Initialize the API with credentials from environment variables."""
        load_dotenv()
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = os.getenv("WEATHER_ENDPOINT")
        
        if not self.api_key or not self.base_url:
            raise ValueError("Missing required environment variables for Weather API")
    
    def get_weather_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the current weather data for the user's location.
        
        Returns:
            Dict: A dictionary containing weather data or None if the request fails
        """
        params = {
            "key": self.api_key
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return self._extract_weather_data(data)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def _extract_weather_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract weather data from the API response.
        
        Args:
            data: The JSON response from the API
            
        Returns:
            Dict: A dictionary containing weather data or None if not found
        """
        try:
            # Store the raw data for later processing
            result = {
                "raw_data": data
            }
            
            # Extract specific fields if they exist
            if "location" in data:
                result["location"] = {
                    "name": data["location"].get("name"),
                    "region": data["location"].get("region"),
                    "country": data["location"].get("country"),
                    "lat": data["location"].get("lat"),
                    "lon": data["location"].get("lon"),
                    "location_time": data["location"].get("localtime")
                }
            
            if "current" in data:
                result["current"] = {
                    "temp_c": data["current"].get("temp_c"),                                        
                    "wind_kph": data["current"].get("wind_kph"),
                    "wind_dir": data["current"].get("wind_dir"),
                    "humidity": data["current"].get("humidity"),
                    "feelslike_c": data["current"].get("feelslike_c"),                    
                    "uv": data["current"].get("uv"),
                    "last_updated": data["current"].get("last_updated")
                }
            
            return result
        except (KeyError, ValueError, TypeError) as e:
            print(f"Error parsing weather data: {e}")
            return None
    
    def get_temperature(self) -> Optional[float]:
        """
        Get the current temperature in Celsius.
        
        Returns:
            float: The current temperature in Celsius, or None if the request fails
        """
        data = self.get_weather_data()
        if data and "current" in data and "temp_c" in data["current"]:
            return data["current"]["temp_c"]
        return None
