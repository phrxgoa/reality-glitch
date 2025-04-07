import sys
from datetime import datetime, timedelta
import blessed
from integration.wrapper_coinmarket import CoinMarketCapAPI
from integration.wrapper_fmp import FmpAPI
from integration.wrapper_weather import WeatherAPI
from db.db_operations import DatabaseOperations
from integration.sync_apis import SyncApis
from ai_engine import StoryEngine
import os

class RealityGlitchGame:        
    def __init__(self):
        """Initialize the game and its components."""
        self.db_ops = DatabaseOperations()
        self.running = True
        self.term = blessed.Terminal()
        self.story_mode = False
        self.story_engine = StoryEngine()
        self.loaded_from_save = False
        
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
        print("Press F1 for help. Press Esc to exit.\n")
        
        # Check if there's a saved story and inform the user
        if self.story_engine.has_saved_story():
            print("\033[32mA saved story was found in the cosmic archives! (Press F10 to load)\033[0m\n")
    
    def display_help(self):
        """Display available commands."""
        print("=== KEYBOARD CONTROLS ===")
        print("F1: Display this help")
        print("F2: Check Bitcoin price")
        print("F3: Check stock market")
        print("F4: Check weather")
        print("F5: Trigger panic event")
        print("F6: Toggle story mode")
        print("F7: Show save file location")
        print("F9: Save story (in story mode)")
        print("F10: Load saved story")
        print("Esc: Exit game")
    
    def handle_story_choice(self, key):
        """Handle player choice in story mode"""
        if key.name == 'KEY_1' or key.name == 'KEY_2' or key.name == 'KEY_3':
            choice_index = int(key.name[-1]) - 1
            if self.story_engine.make_choice(choice_index):
                # Choice was processed successfully
                # The story will be displayed in the main loop
                pass
            else:
                print("\nThe alien device buzzes angrily - even cosmic horrors appreciate valid inputs.")
        elif key.name == 'KEY_ESCAPE':
            self.story_mode = False
            self.display_welcome()
    
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
    
    def toggle_story_mode(self):
        """Toggle between story mode and reality mode"""
        self.story_mode = not self.story_mode
        if self.story_mode:
            if not self.loaded_from_save:
                # Reset the story engine when entering story mode
                self.story_engine.reset()
            else:
                # Reset the loaded flag
                self.loaded_from_save = False
                
            # Clear the screen before displaying the story
            os.system('cls' if os.name == 'nt' else 'clear')
            # Display the story and ensure it returns True to indicate success
            if not self.story_engine.display_story():
                print("\nError: Failed to generate story. Returning to reality mode.")
                self.story_mode = False
                self.display_welcome()
        else:
            self.display_welcome()
    
    def save_story(self):
        """Save the current story"""
        if self.story_mode:
            if self.story_engine.save_story():
                print("\n\033[32mThe alien device glows green as your story is saved to the cosmic archives.\033[0m")
                print("Press any key to continue...")
            else:
                print("\n\033[31mThe alien device sparks and fizzles. Your story couldn't be saved.\033[0m")
                print("Press any key to continue...")
            # Wait for any key
            self.term.inkey()
            
            # Redisplay the story after saving
            os.system('cls' if os.name == 'nt' else 'clear')
            self.story_engine.typewriter_effect(f"\n{self.story_engine.current_story}\n")
            for i, choice in enumerate(self.story_engine.current_choices, 1):
                self.story_engine.typewriter_effect(f"{i}. {choice}", delay=0.05)
            print("\nPress 1, 2, or 3 to make your choice, or Esc to return to reality.")
            print("\033[32mSaved story is available (F10 to load)\033[0m")
        else:
            print("\033[33mStory saving is only available in story mode.\033[0m")
    
    def load_story(self):
        """Load a saved story"""
        if self.story_engine.has_saved_story():
            if self.story_engine.load_story():
                print("\033[32mA familiar cosmic shimmer appears as your saved story materializes...\033[0m")
                # Set flag to prevent reset when entering story mode
                self.loaded_from_save = True
                # Enter story mode
                if not self.story_mode:
                    self.story_mode = True
                    # Clear the screen before displaying the story
                    os.system('cls' if os.name == 'nt' else 'clear')
                    # Display the loaded story and choices manually
                    self.story_engine.typewriter_effect(f"\n{self.story_engine.current_story}\n")
                    for i, choice in enumerate(self.story_engine.current_choices, 1):
                        self.story_engine.typewriter_effect(f"{i}. {choice}", delay=0.05)
                    print("\nPress 1, 2, or 3 to make your choice, or Esc to return to reality.")
                    print("Press F9 to save your adventure or F10 to load a saved one.")
                else:
                    # Already in story mode, just display the loaded story
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.story_engine.typewriter_effect(f"\n{self.story_engine.current_story}\n")
                    for i, choice in enumerate(self.story_engine.current_choices, 1):
                        self.story_engine.typewriter_effect(f"{i}. {choice}", delay=0.05)
                    print("\nPress 1, 2, or 3 to make your choice, or Esc to return to reality.")
                    print("Press F9 to save your adventure or F10 to load a saved one.")
            else:
                print("\033[31mThe cosmic archives appear to be damaged. Failed to load story.\033[0m")
        else:
            print("\033[33mNo saved stories found in the cosmic archives.\033[0m")
    
    def show_save_location(self):
        """Show the location of the save file"""
        save_file = self.story_engine.DEFAULT_SAVE_FILE
        save_dir = os.path.dirname(save_file)
        
        print(f"\n=== SAVE FILE LOCATION ===")
        print(f"Save directory: {os.path.abspath(save_dir)}")
        print(f"Save file: {os.path.abspath(save_file)}")
        
        # Check if directory exists and is writable
        if not os.path.exists(save_dir):
            print("\033[33mSave directory does not exist yet. It will be created when you save.\033[0m")
        elif not os.access(save_dir, os.W_OK):
            print("\033[31mWARNING: Save directory exists but is NOT writable!\033[0m")
            print("Saving will likely fail. Please check permissions.")
        else:
            print("\033[32mSave directory exists and is writable.\033[0m")
            
        # Check if save file exists
        if os.path.exists(save_file):
            print(f"\033[32mA save file exists at this location.\033[0m")
        else:
            print(f"\033[33mNo save file exists yet at this location.\033[0m")
    
    def handle_key(self, key):
        """Handle key press events."""
        if key.name == 'KEY_F1':
            self.display_help()
        elif key.name == 'KEY_F2':
            self.bitcoin()
        elif key.name == 'KEY_F3':
            self.stocks()
        elif key.name == 'KEY_F4':
            self.weather()
        elif key.name == 'KEY_F5':
            self.trigger_panic()
        elif key.name == 'KEY_F6':
            self.toggle_story_mode()
        elif key.name == 'KEY_F7':
            self.show_save_location()
        elif key.name == 'KEY_F9':
            self.save_story()
        elif key.name == 'KEY_F10':
            self.load_story()
        elif key.name == 'KEY_ESCAPE':
            print("\nERROR 666: ESCAPE DENIED. JUST KIDDING. BYE.")
            self.running = False
    
    def run(self):
        """Run the main game loop."""
        self.display_welcome()
        
        # Set terminal to raw mode
        with self.term.cbreak(), self.term.hidden_cursor():
            while self.running:
                if self.story_mode:
                    # Story mode game loop
                    # 1. Display the current story and choices (only if not already displayed)
                    if self.story_engine.display_story():
                        # 2. Wait for player choice
                        while self.running and self.story_mode:
                            key = self.term.inkey()
                            
                            # Handle escape to exit story mode
                            if key.name == 'KEY_ESCAPE':
                                self.story_mode = False
                                self.display_welcome()
                                break
                            
                            # Handle save/load in story mode
                            elif key.name == 'KEY_F9':
                                self.save_story()
                                # No need to redisplay - save_story already handles this
                                continue
                            elif key.name == 'KEY_F10':
                                self.load_story()
                                # Break out of the inner loop to display the loaded story
                                break
                            elif key.name == 'KEY_F7':
                                self.show_save_location()
                                # Wait for any key to continue
                                print("\nPress any key to continue...")
                                self.term.inkey()
                                # Redisplay story
                                os.system('cls' if os.name == 'nt' else 'clear')
                                self.story_engine.typewriter_effect(f"\n{self.story_engine.current_story}\n")
                                for i, choice in enumerate(self.story_engine.current_choices, 1):
                                    self.story_engine.typewriter_effect(f"{i}. {choice}", delay=0.05)
                                print("\nPress 1, 2, or 3 to make your choice, or Esc to return to reality.")
                                print("Press F9 to save your adventure or F10 to load a saved one.")
                                continue
                            elif key:
                                # Handle story choices (1, 2, 3)
                                if key in ['1', '2', '3'] or key.name in ['1', '2', '3'] or key.name in ['KEY_1', 'KEY_2', 'KEY_3']:
                                    # Extract the number from the key
                                    if key in ['1', '2', '3']:
                                        choice_index = int(key) - 1
                                    elif key.name in ['1', '2', '3']:
                                        choice_index = int(key.name) - 1
                                    else:
                                        choice_index = int(key.name[-1]) - 1
                                    
                                    print(f"\nYou chose option {choice_index + 1}...")
                                    
                                    if self.story_engine.make_choice(choice_index):
                                        # Choice was processed successfully, break inner loop to display next story
                                        break
                                    else:
                                        print("\nThe alien device buzzes angrily - even cosmic horrors appreciate valid inputs.")
                                else:
                                    # Provide feedback for invalid keys
                                    print("\nThe alien device doesn't recognize that command. Try 1, 2, or 3.")
                    else:
                        # If display_story returns False, there was an error
                        print("\nError: Failed to generate story. Returning to reality mode.")
                        self.story_mode = False
                        self.display_welcome()
                else:
                    # Reality mode - handle regular commands
                    key = self.term.inkey()
                    self.handle_key(key)

def start_game_cli(debug=False):
    """Entry point for the game."""
    game = RealityGlitchGame()
    # Update the story engine to use debug mode if needed
    game.story_engine = StoryEngine(debug=debug)
    game.run()

if __name__ == "__main__":
    # Check if debug mode is requested via command line
    debug_mode = "--debug" in sys.argv
    start_game_cli(debug=debug_mode)