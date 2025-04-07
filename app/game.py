from datetime import datetime, timedelta
from prompt_toolkit import PromptSession
from wrapper_coinmarket import CoinMarketCapAPI
from wrapper_fmp import FmpAPI
from wrapper_weather import WeatherAPI
from db_operations import DatabaseOperations
from sync_apis import SyncApis

class RealityGlitchGame:        
    def __init__(self):
        """Initialize the game and its components."""
        self.session = PromptSession()        
        self.db_ops = DatabaseOperations()
        
        # Check if this is the first run and sync with APIs if needed
        if self.db_ops.is_first_run():
            print("First run detected. Syncing with APIs...")
            sync = SyncApis()
            sync.sync_all()
            print("Initial sync completed.")
        else:
            # Check if we need to sync on startup
            self.check_and_sync()
    
    def check_and_sync(self):
        """Check if 10 minutes have passed since last sync and sync if needed."""
        last_sync = self.db_ops.get_last_sync_time()           
        if not last_sync or (datetime.now() - last_sync) > timedelta(minutes=10):        
            print("Syncing with APIs...")
            sync = SyncApis()
            sync.sync_all()
    
    def display_welcome(self):
        """Display the welcome message."""
        print("=== REALITYGLITCH ACTIVATED ===")
        print("Type /help for commands. Ctrl+C to exit.\n")
    
    def display_help(self):
        """Display available commands."""
        print("Commands: /btc, /stocks, /weather, /panic, /exit")
    
    def bitcoin(self):
        """Check and display current Bitcoin price and changes."""
        btc_data = self.db_ops.get_latest_bitcoin_data()
        if btc_data:
            print("=== BITCOIN VALUE ===")
            price = btc_data["price_usd"]
            change_1h = btc_data["percent_change_1h"]
            change_24h = btc_data["percent_change_24h"]
            last_updated = btc_data["last_updated"]
            
            # Format timestamp
            try:
                if isinstance(last_updated, datetime):
                    dt = last_updated
                else:
                    dt = datetime.strptime(str(last_updated), "%Y-%m-%d %H:%M:%S.%f")
                formatted_time = dt.strftime("%d/%m/%Y %H:%M:%S")
                last_updated = formatted_time
            except (ValueError, TypeError) as e:
                # Keep original timestamp if formatting fails
                pass
                
            print(f"BTC price: ${price:,.2f}")
            print(f"1h change: {change_1h:.2f}%")
            print(f"24h change: {change_24h:.2f}%")
            print(f"Last updated: {last_updated}")
        else:
            print("ERROR: Unable to fetch BTC data. Reality might be glitching...")
    
    def trigger_panic(self):
        """Trigger a panic event."""
        print("PANIC EVENT TRIGGERED")
    
    def stocks(self):
        """Check and display current stock market indices."""
        indices_data = self.db_ops.get_latest_stock_data()
        if indices_data:
            print("=== STOCK MARKET INDICES ===")                    
            if indices_data:
                timestamp = indices_data[0]["timestamp"]
                try:                    
                    if isinstance(timestamp, datetime):
                        dt = timestamp
                    else:                        
                        dt = datetime.strptime(str(timestamp), "%Y-%m-%d %H:%M:%S.%f")                                        
                    formatted_time = dt.strftime("%d/%m/%Y %H:%M:%S")
                    print(f"Last updated: {formatted_time}")
                except (ValueError, TypeError) as e:                    
                    print(f"Last updated: {timestamp}")
                    print(f"Error: {e}")
            
            for index in indices_data:
                symbol = index["symbol"]
                price = index["price"]
                change = index["change"]
                
                # Calculate percentage of change relative to price
                percentage = (change / price) * 100 if price else 0
                percentage_str = f"+{percentage:.2f}%" if percentage >= 0 else f"{percentage:.2f}%"
                
                print(f"{symbol}: {price:,.2f} => {percentage_str}")
        else:
            print("ERROR: Unable to fetch stock market data. Reality might be glitching...")
    
    def weather(self):
        """Check and display current weather data."""
        weather_data = self.db_ops.get_latest_weather_data()
        if weather_data:
            print("=== WEATHER DATA ===")
            print(f"Location: {weather_data['location_name']}, {weather_data['region']}, {weather_data['country']}")
            print(f"Temperature: {weather_data['temperature_c']}°C (feels like {weather_data['feels_like_c']}°C)")
            print(f"Wind: {weather_data['wind_kph']} km/h {weather_data['wind_direction']}")
            print(f"Humidity: {weather_data['humidity']}%")
            print(f"UV Index: {weather_data['uv_index']}")
            
            # Format timestamp
            last_updated = weather_data['last_updated']
            try:
                if isinstance(last_updated, datetime):
                    dt = last_updated
                else:
                    dt = datetime.strptime(str(last_updated), "%Y-%m-%d %H:%M:%S.%f")
                formatted_time = dt.strftime("%d/%m/%Y %H:%M:%S")
                last_updated = formatted_time
            except (ValueError, TypeError) as e:
                # Keep original timestamp if formatting fails
                pass
                
            print(f"Last updated: {last_updated}")
        else:
            print("ERROR: Unable to fetch weather data. Reality might be glitching...")
    
    def process_command(self, command):
        """Process user commands."""
        # Check if we need to sync before processing any command
        self.check_and_sync()
        
        command = command.strip()
        
        if command == "/help":
            self.display_help()
        elif command == "":
            pass  # Do nothing for empty input
        elif command == "/exit":
            print("ERROR 666: ESCAPE DENIED. JUST KIDDING. BYE.")
            return False
        elif command == "/btc":
            self.bitcoin()
        elif command == "/stocks":
            self.stocks()
        elif command == "/weather":
            self.weather()
        elif command == "/panic":
            self.trigger_panic()
        else:
            print(f"SYNTAX ERROR: '{command}' is chaos... but unrecognized.")
        
        return True
    
    def run(self):
        """Run the main game loop."""
        self.display_welcome()
        
        running = True
        while running:
            try:
                user_input = self.session.prompt("> ")
                running = self.process_command(user_input)
            except KeyboardInterrupt:
                print("\nWARNING: REALITY REASSEMBLING...")
                break

def start_game_cli():
    """Entry point for the game."""
    game = RealityGlitchGame()
    game.run()

if __name__ == "__main__":
    start_game_cli()