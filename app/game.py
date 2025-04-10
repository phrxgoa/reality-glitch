import sys
from datetime import datetime, timedelta
import blessed
import os
import re
import time
import random

# Import refactored modules
from ui import UIRenderer, MenuRenderer, AnimationManager
from input_handler import KeyHandler
from game_state import GameState, SaveManager

# Import existing modules
from integration.wrapper_coinmarket import CoinMarketCapAPI
from integration.wrapper_fmp import FmpAPI
from integration.wrapper_weather import WeatherAPI
from db.db_operations import DatabaseOperations
from integration.sync_apis import SyncApis
from ai_engine import StoryEngine, SAVE_DIR
from integration.reality_data import RealityData

class RealityGlitchGame:        
    def __init__(self, debug=False):
        """Initialize the game and its components."""
        self.term = blessed.Terminal()
        
        # Initialize story engine
        self.story_engine = StoryEngine(debug=debug)
        
        # Initialize UI components
        self.ui_renderer = UIRenderer(self.term)
        self.menu_renderer = MenuRenderer(self.term)
        self.animation_manager = AnimationManager(self.term)
        
        # Initialize game state manager
        self.game_state = GameState(story_engine=self.story_engine, debug=debug)
        
        # Initialize save manager
        self.save_manager = SaveManager(save_dir=SAVE_DIR, story_engine=self.story_engine)
        
        # Initialize input handler
        self.key_handler = KeyHandler(self)
        
        # Set up properties from UI components for convenience
        self.text_color = self.ui_renderer.text_color
        self.highlight = self.ui_renderer.highlight
        self.dim = self.ui_renderer.dim
        self.warning = self.ui_renderer.warning
        self.error = self.ui_renderer.error
        
        # Set up core state variables
        self.running = True
        self.story_mode = False
        self.loaded_from_save = False
        self.save_menu_active = False
        self.load_menu_active = False
        self.current_saves = []
        self.menu_selection = 0
        self.reality_data = RealityData(debug=debug)
        self.db_ops = DatabaseOperations()
        
        # Check if this is the first run and sync with APIs if needed
        self.game_state.check_and_sync()
    
    def display_welcome(self):
        """Display the welcome message with clean terminal aesthetics."""
        self.animation_manager.display_welcome_screen()
    
    def display_help(self):
        """Display help information."""
        self.animation_manager.display_help_screen()
        # Wait for key press
        key = self.term.inkey()
        
        # If ESC is pressed, return to main menu instead of exiting
        if key.name == 'KEY_ESCAPE':
            self.display_welcome()
            return
    
    def display_story(self):
        """Display the current story state with proper formatting"""
        # Clear screen and reset cursor position
        print(self.term.clear + self.term.home)
        
        # Force a redraw of the terminal to ensure clean display
        print(self.term.normal_cursor)
        
        # Call the Story Engine's display_story method which now has the enhanced UI
        return self.story_engine.display_story()

    def handle_story_choice(self, key):
        """Handle player choice in story mode"""
        # This method should delegate to the key handler to avoid duplicate logic
        self.key_handler.handle_story_choice(key)
    
    def bitcoin(self):
        """Check and display current Bitcoin price and changes with reality glitch indicators."""
        # Clear screen
        print(self.term.clear)
        
        # Title
        title = "BITCOIN REALITY FRAGMENT"
        title_x = (self.term.width - len(title)) // 2
        print(self.term.move_xy(title_x, 2) + self.text_color + title + self.term.normal)
        
        btc_data = self.db_ops.get_latest_bitcoin_data()
        if btc_data:
            # Center the content
            content_width = 40
            x = (self.term.width - content_width) // 2
            y = 4
            
            # Format timestamp
            try:
                if isinstance(btc_data["last_updated"], datetime):
                    dt = btc_data["last_updated"]
                else:
                    dt = datetime.strptime(str(btc_data["last_updated"]), "%Y-%m-%d %H:%M:%S.%f")
                formatted_time = dt.strftime("%d/%m/%Y %H:%M:%S")
                last_updated = formatted_time
            except (ValueError, TypeError) as e:
                # Keep original timestamp if formatting fails
                last_updated = btc_data["last_updated"]
            
            # Draw a box around the content
            self.draw_box(x, y, content_width, 8, "BITCOIN DATA")
            
            # Display data with proper formatting
            price = btc_data["price_usd"]
            change_1h = btc_data["percent_change_1h"]
            change_24h = btc_data["percent_change_24h"]
            
            # Determine color for price changes
            change_1h_color = self.term.green if change_1h >= 0 else self.term.red
            change_24h_color = self.term.green if change_24h >= 0 else self.term.red
            
            # Format the changes with + or - sign
            change_1h_str = f"+{change_1h:.2f}%" if change_1h >= 0 else f"{change_1h:.2f}%"
            change_24h_str = f"+{change_24h:.2f}%" if change_24h >= 0 else f"{change_24h:.2f}%"
            
            # Display the data
            print(self.term.move_xy(x + 2, y + 2) + self.highlight + f"BTC Price: " + self.term.normal + f"${price:,.2f}")
            print(self.term.move_xy(x + 2, y + 3) + self.highlight + f"1h Change: " + self.term.normal + change_1h_color + change_1h_str + self.term.normal)
            print(self.term.move_xy(x + 2, y + 4) + self.highlight + f"24h Change: " + self.term.normal + change_24h_color + change_24h_str + self.term.normal)
            print(self.term.move_xy(x + 2, y + 5) + self.highlight + f"Last Updated: " + self.term.normal + self.dim + last_updated + self.term.normal)
            
            # Get reality glitches for bitcoin
            self.reality_data.refresh_data()
            glitches = self.reality_data.get_reality_glitches()
            bitcoin_glitches = glitches["bitcoin"]
            
            # Create a glitch status indicator
            glitch_title = "REALITY GLITCH STATUS"
            glitch_box_width = 60
            glitch_box_x = (self.term.width - glitch_box_width) // 2
            glitch_box_y = y + 10
            
            # Determine glitch intensity based on price change
            glitch_level = "STABLE"
            glitch_color = self.text_color
            
            if abs(change_1h) > 7:
                glitch_level = "SEVERE"
                glitch_color = self.error
            elif abs(change_1h) > 3:
                glitch_level = "MODERATE"
                glitch_color = self.warning
            elif abs(change_1h) > 1:
                glitch_level = "MINOR"
                glitch_color = self.highlight
            
            # Draw glitch status box
            self.draw_box(glitch_box_x, glitch_box_y, glitch_box_width, 5, glitch_title)
            
            # Display glitch status
            print(self.term.move_xy(glitch_box_x + 2, glitch_box_y + 2) + 
                  self.highlight + f"Status: " + glitch_color + glitch_level + self.term.normal)
            
            # Display a random glitch descriptor if available
            if bitcoin_glitches["descriptors"]:
                descriptor = random.choice(bitcoin_glitches["descriptors"])
                print(self.term.move_xy(glitch_box_x + 2, glitch_box_y + 3) + 
                      self.highlight + f"Effect: " + glitch_color + descriptor.capitalize() + self.term.normal)
            
            # Add a cosmic message
            if bitcoin_glitches["events"]:
                cosmic_msg = random.choice(bitcoin_glitches["events"])
            else:
                cosmic_msg = "The digital currency fluctuates in the cosmic void..."
            
            msg_x = (self.term.width - len(cosmic_msg)) // 2
            print(self.term.move_xy(msg_x, glitch_box_y + 7) + self.text_color + cosmic_msg + self.term.normal)
            
            # Show story impact note
            impact_msg = "This data will influence your story experience..."
            impact_x = (self.term.width - len(impact_msg)) // 2
            print(self.term.move_xy(impact_x, glitch_box_y + 9) + self.dim + impact_msg + self.term.normal)
        else:
            # Error message
            error_msg = "ERROR: Unable to fetch BTC data. Reality might be glitching..."
            error_x = (self.term.width - len(error_msg)) // 2
            print(self.term.move_xy(error_x, 5) + self.error + error_msg + self.term.normal)
        
        # Footer
        footer = "Press any key to continue..."
        footer_x = (self.term.width - len(footer)) // 2
        print(self.term.move_xy(footer_x, self.term.height - 2) + self.dim + footer + self.term.normal)
        
        # Wait for key press
        self.term.inkey()
        
        # Redraw the main menu
        self.display_welcome()
    
    def trigger_panic(self):
        """Trigger a panic event that causes multiple reality glitches."""
        self.animation_manager.trigger_panic_animation()
        
        # Force a refresh of reality data in the story engine
        self.story_engine.reality_data.refresh_data()
        
        # Redraw the appropriate screen
        if self.story_mode:
            self.display_story()
        else:
            self.display_welcome()
    
    def stocks(self):
        """Check and display current stock market indices with reality glitch indicators."""
        # Clear screen
        print(self.term.clear)
        
        # Title
        title = "STOCK MARKET REALITY FRAGMENT"
        title_x = (self.term.width - len(title)) // 2
        print(self.term.move_xy(title_x, 2) + self.text_color + title + self.term.normal)
        
        indices_data = self.db_ops.get_latest_stock_data()
        if indices_data:
            # Center the content
            content_width = 50
            x = (self.term.width - content_width) // 2
            y = 4
            
            # Format timestamp
            try:
                if isinstance(indices_data[0]["timestamp"], datetime):
                    dt = indices_data[0]["timestamp"]
                else:
                    dt = datetime.strptime(str(indices_data[0]["timestamp"]), "%Y-%m-%d %H:%M:%S.%f")
                formatted_time = dt.strftime("%d/%m/%Y %H:%M:%S")
                last_updated = formatted_time
            except (ValueError, TypeError) as e:
                # Keep original timestamp if formatting fails
                last_updated = indices_data[0]["timestamp"]
            
            # Draw a box around the content
            self.draw_box(x, y, content_width, len(indices_data) * 2 + 3, "MARKET INDICES")
            
            # Display last updated time
            print(self.term.move_xy(x + 2, y + 2) + self.highlight + f"Last Updated: " + self.term.normal + self.dim + last_updated + self.term.normal)
            
            # Track avg market change for glitch intensity
            total_change_pct = 0
            count = 0
            
            # Display each index
            for i, index in enumerate(indices_data):
                symbol = index["symbol"]
                price = index["price"]
                change = index["change"]
                
                # Calculate percentage of change relative to price
                percentage = (change / price) * 100 if price else 0
                total_change_pct += percentage
                count += 1
                
                percentage_str = f"+{percentage:.2f}%" if percentage >= 0 else f"{percentage:.2f}%"
                
                # Determine color for price changes
                change_color = self.term.green if percentage >= 0 else self.term.red
                
                # Display the index data
                print(self.term.move_xy(x + 2, y + 3 + i * 2) + self.highlight + f"{symbol}: " + self.term.normal + f"${price:,.2f}")
                print(self.term.move_xy(x + 2, y + 4 + i * 2) + self.highlight + f"Change: " + self.term.normal + change_color + percentage_str + self.term.normal)
            
            # Get reality glitches for stocks
            self.reality_data.refresh_data()
            glitches = self.reality_data.get_reality_glitches()
            stock_glitches = glitches["stocks"]
            
            # Calculate average market change
            avg_change = total_change_pct / count if count > 0 else 0
            
            # Create a glitch status indicator
            glitch_title = "REALITY GLITCH STATUS"
            glitch_box_width = 60
            glitch_box_x = (self.term.width - glitch_box_width) // 2
            glitch_box_y = y + len(indices_data) * 2 + 5
            
            # Determine glitch level based on average market change and volatility
            glitch_level = "STABLE"
            glitch_color = self.text_color
            
            if abs(avg_change) > 3:
                glitch_level = "SEVERE"
                glitch_color = self.error
            elif abs(avg_change) > 1.5:
                glitch_level = "MODERATE"
                glitch_color = self.warning
            elif abs(avg_change) > 0.5:
                glitch_level = "MINOR"
                glitch_color = self.highlight
            
            # Add volatility indicator
            volatility_text = stock_glitches["volatility"].upper()
            
            # Draw glitch status box
            self.draw_box(glitch_box_x, glitch_box_y, glitch_box_width, 6, glitch_title)
            
            # Display glitch status
            print(self.term.move_xy(glitch_box_x + 2, glitch_box_y + 2) + 
                  self.highlight + f"Status: " + glitch_color + glitch_level + self.term.normal)
            
            # Display market direction
            direction_text = stock_glitches["market_direction"].replace("_", " ").upper()
            print(self.term.move_xy(glitch_box_x + 2, glitch_box_y + 3) + 
                  self.highlight + f"Market Direction: " + glitch_color + direction_text + self.term.normal)
            
            # Display volatility
            print(self.term.move_xy(glitch_box_x + 2, glitch_box_y + 4) + 
                  self.highlight + f"Volatility: " + glitch_color + volatility_text + self.term.normal)
            
            # Add a cosmic message
            if stock_glitches["events"]:
                cosmic_msg = random.choice(stock_glitches["events"])
            else:
                cosmic_msg = "The market indices pulse with cosmic energy..."
            
            msg_x = (self.term.width - len(cosmic_msg)) // 2
            print(self.term.move_xy(msg_x, glitch_box_y + 8) + self.text_color + cosmic_msg + self.term.normal)
            
            # Show story impact note
            impact_msg = "This data will influence your story experience..."
            impact_x = (self.term.width - len(impact_msg)) // 2
            print(self.term.move_xy(impact_x, glitch_box_y + 10) + self.dim + impact_msg + self.term.normal)
        else:
            # Error message
            error_msg = "ERROR: Unable to fetch stock market data. Reality might be glitching..."
            error_x = (self.term.width - len(error_msg)) // 2
            print(self.term.move_xy(error_x, 5) + self.error + error_msg + self.term.normal)
        
        # Footer
        footer = "Press any key to continue..."
        footer_x = (self.term.width - len(footer)) // 2
        print(self.term.move_xy(footer_x, self.term.height - 2) + self.dim + footer + self.term.normal)
        
        # Wait for key press
        self.term.inkey()
        
        # Redraw the main menu
        self.display_welcome()
    
    def weather(self):
        """Check and display current weather data with reality glitch indicators."""
        # Clear screen
        print(self.term.clear)
        
        # Title
        title = "WEATHER REALITY FRAGMENT"
        title_x = (self.term.width - len(title)) // 2
        print(self.term.move_xy(title_x, 2) + self.text_color + title + self.term.normal)
        
        weather_data = self.db_ops.get_latest_weather_data()
        if weather_data:
            # Center the content
            content_width = 50
            x = (self.term.width - content_width) // 2
            y = 4
            
            # Format timestamp
            try:
                if isinstance(weather_data['last_updated'], datetime):
                    dt = weather_data['last_updated']
                else:
                    dt = datetime.strptime(str(weather_data['last_updated']), "%Y-%m-%d %H:%M:%S.%f")
                formatted_time = dt.strftime("%d/%m/%Y %H:%M:%S")
                last_updated = formatted_time
            except (ValueError, TypeError) as e:
                # Keep original timestamp if formatting fails
                last_updated = weather_data['last_updated']
            
            # Draw a box around the content
            self.draw_box(x, y, content_width, 9, "WEATHER DATA")
            
            # Display the data
            print(self.term.move_xy(x + 2, y + 2) + self.highlight + f"Location: " + self.term.normal + f"{weather_data['location_name']}, {weather_data['region']}, {weather_data['country']}")
            print(self.term.move_xy(x + 2, y + 3) + self.highlight + f"Temperature: " + self.term.normal + f"{weather_data['temperature_c']}°C (feels like {weather_data['feels_like_c']}°C)")
            print(self.term.move_xy(x + 2, y + 4) + self.highlight + f"Wind: " + self.term.normal + f"{weather_data['wind_kph']} km/h {weather_data['wind_direction']}")
            print(self.term.move_xy(x + 2, y + 5) + self.highlight + f"Humidity: " + self.term.normal + f"{weather_data['humidity']}%")
            print(self.term.move_xy(x + 2, y + 6) + self.highlight + f"UV Index: " + self.term.normal + f"{weather_data['uv_index']}")
            print(self.term.move_xy(x + 2, y + 7) + self.highlight + f"Last Updated: " + self.term.normal + self.dim + last_updated + self.term.normal)
            
            # Get reality glitches for weather
            self.reality_data.refresh_data()
            glitches = self.reality_data.get_reality_glitches()
            weather_glitches = glitches["weather"]
            
            # Create a glitch status indicator
            glitch_title = "REALITY GLITCH STATUS"
            glitch_box_width = 60
            glitch_box_x = (self.term.width - glitch_box_width) // 2
            glitch_box_y = y + 11
            
            # Determine glitch level based on temperature extremes
            temp = weather_data['temperature_c']
            glitch_level = "STABLE"
            glitch_color = self.text_color
            
            if temp > 35 or temp < -10:
                glitch_level = "SEVERE"
                glitch_color = self.error
            elif temp > 30 or temp < 0:
                glitch_level = "MODERATE"
                glitch_color = self.warning
            elif temp > 25 or temp < 5:
                glitch_level = "MINOR"
                glitch_color = self.highlight
            
            # Draw glitch status box
            self.draw_box(glitch_box_x, glitch_box_y, glitch_box_width, 6, glitch_title)
            
            # Display glitch status
            print(self.term.move_xy(glitch_box_x + 2, glitch_box_y + 2) + 
                  self.highlight + f"Status: " + glitch_color + glitch_level + self.term.normal)
            
            # Display condition
            condition_text = weather_glitches["condition"].upper()
            print(self.term.move_xy(glitch_box_x + 2, glitch_box_y + 3) + 
                  self.highlight + f"Condition: " + glitch_color + condition_text + self.term.normal)
            
            # Display random weather descriptor if available
            if weather_glitches["descriptors"]:
                descriptor = random.choice(weather_glitches["descriptors"])
                print(self.term.move_xy(glitch_box_x + 2, glitch_box_y + 4) + 
                      self.highlight + f"Effect: " + glitch_color + descriptor.capitalize() + self.term.normal)
            
            # Add a cosmic message
            if weather_glitches["events"]:
                cosmic_msg = random.choice(weather_glitches["events"])
            else:
                cosmic_msg = "The weather patterns shift like cosmic tides..."
            
            msg_x = (self.term.width - len(cosmic_msg)) // 2
            print(self.term.move_xy(msg_x, glitch_box_y + 8) + self.text_color + cosmic_msg + self.term.normal)
            
            # Show story impact note
            impact_msg = "This data will influence your story experience..."
            impact_x = (self.term.width - len(impact_msg)) // 2
            print(self.term.move_xy(impact_x, glitch_box_y + 10) + self.dim + impact_msg + self.term.normal)
        else:
            # Error message
            error_msg = "ERROR: Unable to fetch weather data. Reality might be glitching..."
            error_x = (self.term.width - len(error_msg)) // 2
            print(self.term.move_xy(error_x, 5) + self.error + error_msg + self.term.normal)
        
        # Footer
        footer = "Press any key to continue..."
        footer_x = (self.term.width - len(footer)) // 2
        print(self.term.move_xy(footer_x, self.term.height - 2) + self.dim + footer + self.term.normal)
        
        # Wait for key press
        self.term.inkey()
        
        # Redraw the main menu
        self.display_welcome()
    
    def draw_box(self, x, y, width, height, title=""):
        """Draw a box with optional title."""
        print(self.ui_renderer.draw_box(x, y, width, height, title))
    
    def toggle_story_mode(self):
        """Toggle between story mode and reality mode"""
        self.story_mode = self.game_state.toggle_story_mode()
        
        if self.story_mode:
            # Display the initial story state
            if not self.display_story():
                print("\n" + self.error + "Error: Failed to generate story. Returning to reality mode." + self.term.normal)
                time.sleep(2)
                self.story_mode = False
                self.display_welcome()
        else:
            self.display_welcome()
    
    def save_story(self):
        """Save the current story with menu for selecting save slot"""
        if self.story_mode:
            # Set the save menu to active
            self.save_menu_active = True
            self.menu_selection = 0
            
            # Get existing saves
            self.current_saves = self.save_manager.get_save_files()
            
            # Display save menu
            os.system('cls' if os.name == 'nt' else 'clear')
            self.display_save_menu()
            
            # Wait for user selection handled by key handler
        else:
            print("\033[33mStory saving is only available in story mode.\033[0m")
    
    def display_save_menu(self):
        """Display the save game menu with a split screen layout"""
        self.menu_renderer.display_save_menu(self.current_saves, self.menu_selection, self.story_engine)
    
    def load_story(self):
        """Load a saved story with menu for selecting save slot"""
        # Check if there are any saves
        if not self.save_manager.has_saved_story():
            print("\033[33mNo saved stories found in the cosmic archives.\033[0m")
            return
        
        # Set the load menu to active
        self.load_menu_active = True
        self.menu_selection = 0
        
        # Get existing saves
        self.current_saves = self.save_manager.get_save_files()
        
        # Display load menu
        os.system('cls' if os.name == 'nt' else 'clear')
        self.display_load_menu()
        
        # Wait for user selection handled by key handler
    
    def display_load_menu(self):
        """Display the load game menu with a split screen layout"""
        self.menu_renderer.display_load_menu(self.current_saves, self.menu_selection)
    
    def show_save_location(self):
        """Show the location where save files are stored."""
        save_path = os.path.abspath(self.story_engine.SAVE_DIR)
        print(f"\nSave files are stored in: {save_path}")
        
        # Print some tips
        print(self.dim + "\nTip: These files can be backed up manually if desired." + self.term.normal)
        print(self.dim + "     Do not modify save files manually - this may corrupt them." + self.term.normal)
    
    def handle_key(self, key):
        """Handle key presses."""
        # Delegate all key handling to the KeyHandler instance
        self.key_handler.handle_key(key)
    
    def display_sci_fi_animation(self, duration=5):
        """Display an immersive sci-fi loading animation"""
        self.animation_manager.display_sci_fi_animation(duration)
        
        # Show the appropriate screen
        if self.story_mode:
            self.display_story()
        else:
            self.display_welcome()

    def run(self):
        """Run the main game loop."""
        self.display_welcome()
        
        # Track the last typewriter state to detect transitions
        last_typewriter_active = False
        
        # Set terminal to raw mode
        with self.term.cbreak(), self.term.hidden_cursor():
            while self.running:
                # Check if typewriter just started (transition from inactive to active)
                if self.story_engine.typewriter_active and not last_typewriter_active:
                    # Clear any pending input when typewriter starts
                    while self.term.inkey(timeout=0):
                        pass
                
                # Update the last typewriter state
                last_typewriter_active = self.story_engine.typewriter_active
                
                # Wait for a keypress with a short timeout
                # Use shorter timeout if typewriter is active to check more frequently
                timeout = 0.001 if self.story_engine.typewriter_active else 0.01
                key = self.term.inkey(timeout=timeout)
                
                # Skip processing if no key was pressed
                if not key:
                    continue
                
                # Process keyboard input using KeyHandler
                self.key_handler.handle_key(key)

def start_game_cli(debug=False):
    """Entry point for the game."""
    try:
        game = RealityGlitchGame(debug=debug)
        
        # Show the sci-fi animation at the start
        game.display_sci_fi_animation(duration=4)
        
        # Run the game loop - this will display the welcome screen
        # since the animation now clears and calls display_welcome()
        game.run()
        
    except KeyboardInterrupt:
        print("\nGame terminated by user.")
    except Exception as e:
        print(f"\nError: {e}")
        if debug:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Check if debug mode is requested via command line
    debug_mode = "--debug" in sys.argv
    start_game_cli(debug=debug_mode)