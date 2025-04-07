from db.db_utils import DatabaseConnection, update_last_sync_time
from typing import Dict, Any, List, Optional
from datetime import datetime

class DatabaseOperations:
    """A class to handle database operations for the Reality Glitch game."""
    
    def __init__(self):
        """Initialize the database operations."""
        self.db = DatabaseConnection()
    
    def get_last_sync_time(self) -> Optional[datetime]:
        """
        Get the timestamp of the last sync from the database.
        
        Returns:
            Optional[datetime]: The timestamp of the last sync or None if no sync has been recorded
        """
        query = """
        SELECT timestamp
        FROM last_sync
        ORDER BY id DESC
        LIMIT 1
        """
 
        result = self.db.fetch_one(query)     
        return result.get('timestamp') if result else None
    
    def update_last_sync_time(self) -> bool:
        """
        Update the last sync time in the database by inserting a new record.
        
        Returns:
            bool: True if successful, False otherwise
        """
        return update_last_sync_time()
    
    def is_first_run(self) -> bool:
        """
        Check if this is the first run of the application by checking if there's any data in the database.
        
        Returns:
            bool: True if this is the first run (no data in any table), False otherwise
        """
        # Check if there's any data in the bitcoin table
        btc_query = """
        SELECT COUNT(*) FROM coinmarket_bitcoin_data
        """
        btc_count = self.db.fetch_one(btc_query)
        
        # Check if there's any data in the stock market table
        stocks_query = """
        SELECT COUNT(*) FROM fmp_index_data
        """
        stocks_count = self.db.fetch_one(stocks_query)
        
        # Check if there's any data in the weather table
        weather_query = """
        SELECT COUNT(*) FROM weather_data
        """
        weather_count = self.db.fetch_one(weather_query)
        
        # If all tables are empty, this is the first run
        return (btc_count is None or btc_count.get('count', 0) == 0) and \
               (stocks_count is None or stocks_count.get('count', 0) == 0) and \
               (weather_count is None or weather_count.get('count', 0) == 0)
    
    def get_latest_bitcoin_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest Bitcoin data from the database.
        
        Returns:
            Optional[Dict[str, Any]]: The latest Bitcoin data or None if not found
        """
        query = """
        SELECT price_usd, percent_change_1h, percent_change_24h, last_updated
        FROM coinmarket_bitcoin_data
        ORDER BY timestamp DESC
        LIMIT 1
        """
        return self.db.fetch_one(query)
    
    def get_latest_stock_data(self) -> List[Dict[str, Any]]:
        """
        Get the latest stock market data from the database for specific symbols.
        Returns only the most recent entry for each symbol.
        
        Returns:
            List[Dict[str, Any]]: The latest stock market data for ^IXIC, ^RUT, ^NYA, ^SPX, and ^DJI,
            with only one entry per symbol (the most recent)
        """
        query = """
        WITH RankedData AS (
            SELECT 
                symbol, 
                price, 
                change, 
                volume, 
                timestamp,
                ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY timestamp DESC) as rn
            FROM fmp_index_data
            WHERE symbol IN ('^IXIC', '^RUT', '^NYA', '^SPX', '^DJI')
        )
        SELECT symbol, price, change, volume, timestamp
        FROM RankedData
        WHERE rn = 1
        ORDER BY symbol
        """
        return self.db.fetch_all(query)
    
    def get_latest_weather_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest weather data from the database.
        
        Returns:
            Optional[Dict[str, Any]]: The latest weather data or None if not found
        """
        query = """
        SELECT location_name, region, country, latitude, longitude, location_time,
               temperature_c, wind_kph, wind_direction, humidity, feels_like_c, 
               uv_index, last_updated
        FROM weather_data
        ORDER BY timestamp DESC
        LIMIT 1
        """
        return self.db.fetch_one(query) 