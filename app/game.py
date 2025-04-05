from prompt_toolkit import PromptSession
from wrapper_coinmarket import CoinMarketCapAPI
from wrapper_fmp import FmpAPI
from wrapper_weather import WeatherAPI

class RealityGlitchGame:        
    def __init__(self):
        """Initialize the game and its components."""
        self.session = PromptSession()
        self.btc_api = None
        self.stocks_api = None
        self.weather_api = None
        self.initialize_apis()
    
    def initialize_apis(self):
        """Initialize external APIs and services."""
        try:
            self.btc_api = CoinMarketCapAPI()
        except ValueError as e:
            print(f"ERROR: {e}")
            print("REALITY GLITCH: Unable to initialize cryptocurrency tracking.")
            self.btc_api = None
            
        try:
            self.stocks_api = FmpAPI()
        except ValueError as e:
            print(f"ERROR: {e}")
            print("REALITY GLITCH: Unable to initialize stock market tracking.")
            self.stocks_api = None
            
        try:
            self.weather_api = WeatherAPI()
        except ValueError as e:
            print(f"ERROR: {e}")
            print("REALITY GLITCH: Unable to initialize weather tracking.")
            self.weather_api = None
    
    def display_welcome(self):
        """Display the welcome message."""
        print("=== REALITYGLITCH ACTIVATED ===")
        print("Type /help for commands. Ctrl+C to exit.\n")
    
    def display_help(self):
        """Display available commands."""
        print("Commands: /btc, /stocks, /weather, /panic, /exit")
    
    def bitcoin(self):
        """Check and display current Bitcoin price and changes."""
        if not self.btc_api:
            print("ERROR: Cryptocurrency tracking is not available. Reality is too glitched.")
            return
            
        btc_data = self.btc_api.get_bitcoin_data()
        if btc_data:
            print("=== BITCOIN VALUE ===")
            price = btc_data["price"]
            change_1h = btc_data["percent_change_1h"]
            change_24h = btc_data["percent_change_24h"]
            last_updated = btc_data["last_updated"]
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
        if not self.stocks_api:
            print("ERROR: Stock market tracking is not available. Reality is too glitched.")
            return
            
        indices_data = self.stocks_api.get_index_quotes()
        if indices_data:
            print("=== STOCK MARKET INDICES ===")
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
        if not self.weather_api:
            print("ERROR: Weather tracking is not available. Reality is too glitched.")
            return
            
        weather_data = self.weather_api.get_weather_data()
        if weather_data:
            print("=== WEATHER DATA ===")
            print("Raw weather data:")
            print(weather_data)
        else:
            print("ERROR: Unable to fetch weather data. Reality might be glitching...")
    
    def process_command(self, command):
        """Process user commands."""
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