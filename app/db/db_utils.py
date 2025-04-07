import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Load environment variables
load_dotenv()

class DatabaseConnection:
    """A class to manage database connections."""
    
    def __init__(self):
        """Initialize the database connection."""
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to the database."""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "db"),
                port=os.getenv("POSTGRES_PORT", "5432"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                database=os.getenv("POSTGRES_DB", "reality_glitch")
            )
            self.cursor = self.conn.cursor(cursor_factory=DictCursor)
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the database."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def commit(self):
        """Commit the current transaction."""
        if self.conn:
            self.conn.commit()
    
    def rollback(self):
        """Rollback the current transaction."""
        if self.conn:
            self.conn.rollback()
    
    def execute(self, query: str, params: Optional[tuple] = None):
        """Execute a query."""
        if not self.conn or not self.cursor:
            if not self.connect():
                return False
        
        try:
            self.cursor.execute(query, params)
            return True
        except Exception as e:
            print(f"Error executing query: {e}")
            self.rollback()
            return False
    
    def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Fetch all results from a query."""
        if not self.conn or not self.cursor:
            if not self.connect():
                return []
        
        try:
            self.cursor.execute(query, params)
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching results: {e}")
            return []
    
    def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Fetch one result from a query."""
        if not self.conn or not self.cursor:
            if not self.connect():
                return None
        
        try:
            self.cursor.execute(query, params)
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"Error fetching result: {e}")
            return None


# FMP API Database Functions
def save_fmp_index_data(index_data: List[Dict[str, Any]]) -> bool:
    """
    Save FMP index data to the database.
    
    Args:
        index_data: List of dictionaries containing index data
        
    Returns:
        bool: True if successful, False otherwise
    """
    db = DatabaseConnection()
    
    try:
        for index in index_data:
            query = """
            INSERT INTO fmp_index_data (symbol, price, change, volume)
            VALUES (%s, %s, %s, %s)
            """
            params = (
                index.get("symbol"),
                index.get("price"),
                index.get("change"),
                index.get("volume")
            )
            
            if not db.execute(query, params):
                return False
        
        db.commit()
        return True
    
    except Exception as e:
        print(f"Error saving FMP index data: {e}")
        db.rollback()
        return False
    
    finally:
        db.disconnect()


# Weather API Database Functions
def save_weather_data(weather_data: Dict[str, Any]) -> bool:
    """
    Save weather data to the database.
    
    Args:
        weather_data: Dictionary containing weather data
        
    Returns:
        bool: True if successful, False otherwise
    """
    db = DatabaseConnection()
    
    try:
        location = weather_data.get("location", {})
        current = weather_data.get("current", {})
        
        query = """
        INSERT INTO weather_data (
            location_name, region, country, latitude, longitude, location_time,
            temperature_c, wind_kph, wind_direction,
            humidity, feels_like_c, uv_index, last_updated
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Parse location_time and last_updated if they are strings
        location_time = location.get("location_time")
        if isinstance(location_time, str):
            try:
                location_time = datetime.fromisoformat(location_time.replace("Z", "+00:00"))
            except ValueError:
                location_time = None
        
        last_updated = current.get("last_updated")
        if isinstance(last_updated, str):
            try:
                last_updated = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
            except ValueError:
                last_updated = None
        
        params = (
            location.get("name"),
            location.get("region"),
            location.get("country"),
            location.get("lat"),
            location.get("lon"),
            location_time,
            current.get("temp_c"),            
            current.get("wind_kph"),
            current.get("wind_dir"),
            current.get("humidity"),
            current.get("feelslike_c"),
            current.get("uv"),
            last_updated
        )
        
        if not db.execute(query, params):
            return False
        
        db.commit()
        return True
    
    except Exception as e:
        print(f"Error saving weather data: {e}")
        db.rollback()
        return False
    
    finally:
        db.disconnect()


# CoinMarket API Database Functions
def save_bitcoin_data(bitcoin_data: Dict[str, Any]) -> bool:
    """
    Save Bitcoin data to the database.
    
    Args:
        bitcoin_data: Dictionary containing Bitcoin data
        
    Returns:
        bool: True if successful, False otherwise
    """
    db = DatabaseConnection()
    
    try:
        query = """
        INSERT INTO coinmarket_bitcoin_data (
            price_usd, percent_change_1h, percent_change_24h, last_updated
        )
        VALUES (%s, %s, %s, %s)
        """
        
        # Parse last_updated if it's a string
        last_updated = bitcoin_data.get("last_updated")
        if isinstance(last_updated, str):
            try:
                last_updated = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
            except ValueError:
                last_updated = None
        
        params = (
            bitcoin_data.get("price"),
            bitcoin_data.get("percent_change_1h"),
            bitcoin_data.get("percent_change_24h"),
            last_updated
        )
        
        if not db.execute(query, params):
            return False
        
        db.commit()
        return True
    
    except Exception as e:
        print(f"Error saving Bitcoin data: {e}")
        db.rollback()
        return False
    
    finally:
        db.disconnect()


# Last Sync Database Functions
def update_last_sync_time() -> bool:
    """
    Update the last sync time in the database by inserting a new record.
    The timestamp is set to 3 hours before the current UTC time.
    
    Returns:
        bool: True if successful, False otherwise
    """
    db = DatabaseConnection()
    
    try:
        query = """
        INSERT INTO last_sync (timestamp)
        VALUES (CURRENT_TIMESTAMP - INTERVAL '3 hours')
        """
        
        if not db.execute(query):
            return False
        
        db.commit()
        return True
    
    except Exception as e:
        print(f"Error saving last_sync data: {e}")
        db.rollback()
        return False
    
    finally:
        db.disconnect() 