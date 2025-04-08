import os
import time
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Import API wrappers
from integration.wrapper_fmp import FmpAPI
from integration.wrapper_weather import WeatherAPI
from integration.wrapper_coinmarket import CoinMarketCapAPI

# Import database utilities
from db.db_utils import save_fmp_index_data, save_weather_data, save_bitcoin_data
from db.db_operations import DatabaseOperations

# Load environment variables
load_dotenv()

class SyncApis:
    """Class to handle synchronization of data from various APIs to the database."""
    
    def __init__(self):
        """Initialize the SyncApis class."""
        # Initialize API clients
        self.fmp_api = FmpAPI()
        self.weather_api = WeatherAPI()
        self.coinmarket_api = CoinMarketCapAPI()
        self.db_ops = DatabaseOperations()
    
    def sync_all(self):
        """Sync data from all APIs to the database."""        
        
        # Collect and save data from each API
        try:
            # FMP API - Get index quotes            
            index_quotes = self.fmp_api.get_index_quotes()
            if index_quotes:                
                if save_fmp_index_data(index_quotes):
                    pass
                    #print("Successfully saved FMP index data to database")
                else:
                    pass
                    #print("Failed to save FMP index data to database")
            else:
                pass
                #print("Failed to retrieve FMP index quotes")
            
            # Weather API - Get weather data            
            weather_data = self.weather_api.get_weather_data()
            if weather_data:                
                if save_weather_data(weather_data):
                    pass
                    #print("Successfully saved weather data to database")
                else:
                    pass
                    #print("Failed to save weather data to database")
            else:
                pass
                #print("Failed to retrieve weather data")
            
            # CoinMarket API - Get Bitcoin data            
            bitcoin_data = self.coinmarket_api.get_bitcoin_data()
            if bitcoin_data:                
                if save_bitcoin_data(bitcoin_data):
                    pass
                    #print("Successfully saved Bitcoin data to database")
                else:
                    pass
                    #print("Failed to save Bitcoin data to database")
            else:
                pass
                #print("Failed to retrieve Bitcoin data")
            
            # Update the last sync time after successful completion
            self.db_ops.update_last_sync_time()            
        
        except Exception as e:
            pass
           # print(f"Error in sync_all function: {e}")

if __name__ == "__main__":
    SyncApis() 