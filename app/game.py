import sys
from datetime import datetime, timedelta
import blessed
from integration.wrapper_coinmarket import CoinMarketCapAPI
from integration.wrapper_fmp import FmpAPI
from integration.wrapper_weather import WeatherAPI
from db.db_operations import DatabaseOperations
from integration.sync_apis import SyncApis
from ai_engine import StoryEngine, SAVE_DIR
import os
import re
import time

class RealityGlitchGame:        
    def __init__(self):
        """Initialize the game and its components."""
        self.db_ops = DatabaseOperations()
        self.running = True
        self.term = blessed.Terminal()
        self.story_mode = False
        self.story_engine = StoryEngine()
        self.loaded_from_save = False
        self.save_menu_active = False
        self.load_menu_active = False
        self.current_saves = []
        self.menu_selection = 0
        
        # Simplified color scheme inspired by terminal aesthetics
        self.text_color = self.term.teal  # Main text color
        self.highlight = self.term.white  # For emphasis
        self.dim = self.term.dim  # For less important text
        self.warning = self.term.yellow  # For warnings/important info
        self.error = self.term.red  # For errors
        
        # Check if this is the first run and sync with APIs if needed
        if self.db_ops.is_first_run():
            print(self.text_color + "First run detected. Syncing with APIs..." + self.term.normal)
            sync = SyncApis()
            sync.sync_all()
            print(self.text_color + "Initial sync completed." + self.term.normal)
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
        """Display the welcome message with clean terminal aesthetics."""
        # Clear screen
        print(self.term.clear)
                
        title_art = """
██████╗ ███████╗ █████╗ ██╗     ██╗████████╗██╗   ██╗     ██████╗ ██╗     ██╗████████╗ ██████╗██╗  ██╗
██╔══██╗██╔════╝██╔══██╗██║     ██║╚══██╔══╝╚██╗ ██╔╝    ██╔════╝ ██║     ██║╚══██╔══╝██╔════╝██║  ██║
██████╔╝█████╗  ███████║██║     ██║   ██║    ╚████╔╝     ██║  ███╗██║     ██║   ██║   ██║     ███████║
██╔══██╗██╔══╝  ██╔══██║██║     ██║   ██║     ╚██╔╝      ██║   ██║██║     ██║   ██║   ██║     ██╔══██║
██║  ██║███████╗██║  ██║███████╗██║   ██║      ██║       ╚██████╔╝███████╗██║   ██║   ╚██████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝      ╚═╝        ╚═════╝ ╚══════╝╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝"""
        
        # Center the ASCII art
        lines = title_art.split('\n')
        max_width = max(len(line) for line in lines)
        x = (self.term.width - max_width) // 2
        y = 2
        
        # Print title with teal color
        for line in lines:
            if line.strip():  # Only print non-empty lines
                padding = (max_width - len(line)) // 2
                print(self.term.move_xy(x + padding, y) + self.text_color + line + self.term.normal)
            y += 1
        
        # Subtitle
        subtitle = "A Cosmic Horror Adventure"
        subtitle_x = (self.term.width - len(subtitle)) // 2
        print(self.term.move_xy(subtitle_x, y+1) + self.highlight + subtitle + self.term.normal)
        
        # Instructions
        instructions = "Press F1 for help. Press Esc to exit."
        instr_x = (self.term.width - len(instructions)) // 2
        print(self.term.move_xy(instr_x, y+3) + self.dim + instructions + self.term.normal)
        
        # Check for saved stories
        if self.story_engine.has_saved_story():
            saved_games = self.story_engine.get_save_files()
            count = len(saved_games)
            if count > 0:
                msg = f"{count} reality fragment{'s' if count > 1 else ''} found in the cosmic archives!"
                msg_x = (self.term.width - len(msg)) // 2
                print(self.term.move_xy(msg_x, y+5) + self.text_color + msg + self.term.normal)
                
                help_msg = "Press F10 to load or F8 to view all fragments."
                help_x = (self.term.width - len(help_msg)) // 2
                print(self.term.move_xy(help_x, y+6) + self.dim + help_msg + self.term.normal)
            else:
                msg = "A saved story was found in the cosmic archives!"
                msg_x = (self.term.width - len(msg)) // 2
                print(self.term.move_xy(msg_x, y+5) + self.text_color + msg + self.term.normal)
    
    def display_help(self):
        """Display available commands with clean terminal aesthetics."""
        # Clear screen
        print(self.term.clear)
        
        # Title
        title = "KEYBOARD CONTROLS"
        title_x = (self.term.width - len(title)) // 2
        print(self.term.move_xy(title_x, 2) + self.text_color + title + self.term.normal)
        
        # Commands with descriptions
        commands = [
            ("F1", "Display this help"),
            ("F2", "Check Bitcoin price"),
            ("F3", "Check stock market"),
            ("F4", "Check weather"),
            ("F5", "Trigger panic event"),
            ("F6", "Toggle story mode"),
            ("F7", "Show save file location"),
            ("F8", "View save game list"),
            ("F9", "Save story (in story mode)"),
            ("F10", "Load saved story"),
            ("Esc", "Exit game")
        ]
        
        # Calculate layout
        max_key_width = max(len(cmd[0]) for cmd in commands)
        max_desc_width = max(len(cmd[1]) for cmd in commands)
        total_width = max_key_width + max_desc_width + 6  # Extra space for formatting
        
        # Center the command list
        x = (self.term.width - total_width) // 2
        y = 4
        
        # Draw commands with consistent styling
        for i, (key, desc) in enumerate(commands):
            print(self.term.move_xy(x, y+i) + 
                  self.text_color + f"{key:>{max_key_width}}" + self.term.normal + 
                  self.dim + "  →  " + self.term.normal + 
                  self.highlight + desc)
        
        # Footer
        footer = "Press any key to continue..."
        footer_x = (self.term.width - len(footer)) // 2
        print(self.term.move_xy(footer_x, y + len(commands) + 2) + 
              self.dim + footer + self.term.normal)
    
    def display_story(self):
        """Display the current story state with proper formatting"""
        # Clear screen
        print(self.term.clear)
        print("\n" * 2)  # Add some padding
        
        # If we don't have choices yet, generate the initial story segment
        if not self.story_engine.current_choices:
            # Show loading status
            print(self.warning + "Generating story..." + self.term.normal)
            
            # Check if we have the initial story already from reset
            if self.story_engine.current_story == self.story_engine.messages[1]["content"]:
                # This is the initial story from reset, we need to generate choices
                try:
                    response = self.story_engine.generate_story()
                    new_story, new_choices = self.story_engine.parse_response(response)
                    
                    if new_choices and len(new_choices) >= 3:
                        # Successfully got choices for the initial story
                        self.story_engine.current_choices = new_choices
                        # Update message history with the response that includes choices
                        formatted_content = f"Story: {self.story_engine.current_story}\n\nChoices:\n" + "\n".join([f"{i+1}. {c}" for i, c in enumerate(new_choices)])
                        self.story_engine.messages.append({"role": "assistant", "content": formatted_content})
                    else:
                        print(self.error + "\nError: Failed to generate valid choices." + self.term.normal)
                        return False
                except Exception as e:
                    print(self.error + f"\nError generating story: {e}" + self.term.normal)
                    return False
            else:
                # Need to generate both story and choices
                try:
                    response = self.story_engine.generate_story()
                    new_story, new_choices = self.story_engine.parse_response(response)
                    
                    if new_choices and len(new_choices) >= 3:
                        self.story_engine.current_story = new_story
                        self.story_engine.current_choices = new_choices
                        # Update message history
                        formatted_content = f"Story: {new_story}\n\nChoices:\n" + "\n".join([f"{i+1}. {c}" for i, c in enumerate(new_choices)])
                        self.story_engine.messages.append({"role": "assistant", "content": formatted_content})
                    else:
                        print(self.error + "\nError: Failed to generate valid story and choices." + self.term.normal)
                        return False
                except Exception as e:
                    print(self.error + f"\nError generating story: {e}" + self.term.normal)
                    return False
        
        # Display the story with separators
        #print("=" * 80 + "\n")
        story_lines = self._wrap_text(self.story_engine.current_story, self.term.width - 4)
        for line in story_lines:
            self.story_engine.typewriter_effect(line.strip(), style=self.text_color)
        #print("\n" + "=" * 80 + "\n")
        
        # Display choices with clean numbering
        print("\nWhat would you like to do?\n")
        for i, choice in enumerate(self.story_engine.current_choices, 1):
            self.story_engine.typewriter_effect(f"{i}. {choice}", delay=0.01, style=self.highlight)
        
        # Display instructions
        print("\n" + self.dim + "Press 1, 2, or 3 to make your choice..." + self.term.normal)
        print(self.dim + "Press Esc to return to reality." + self.term.normal)
        print(self.dim + "Press F9 to save your adventure or F10 to load a saved one." + self.term.normal)
        return True

    def handle_story_choice(self, key):
        """Handle player choice in story mode"""
        try:
            choice_index = -1
            if key.name == 'KEY_1' or key.name == 'KEY_2' or key.name == 'KEY_3':
                choice_index = int(key.name[-1]) - 1
                print(f"\nProcessing choice {choice_index+1}...")
            elif key.name == 'KEY_ESCAPE':
                self.story_mode = False
                self.display_welcome()
                return
            
            # Validate choice index
            if choice_index < 0 or choice_index >= len(self.story_engine.current_choices):
                print("\n" + self.error + "Invalid choice number. Please try again." + self.term.normal)
                time.sleep(1)
                self.display_story()
                return
                
            # Clear screen
            print(self.term.clear)
            print("\n" * 2)  # Add some padding at the top
            
            # Show the choice being made
            chosen_action = self.story_engine.current_choices[choice_index]
            self.story_engine.typewriter_effect(f"You chose: {chosen_action}", style=self.text_color)
            time.sleep(0.5)
            
            # Show loading status
            print("\n" + self.warning + "Generating response..." + self.term.normal)
            
            # Process the choice
            success, new_story, new_choices = self.story_engine.make_choice(choice_index)
            
            if success and new_story and new_choices and len(new_choices) >= 3:
                # Display the new story state
                print(self.term.clear)
                print("\n" * 2)  # Add some padding at the top
                
                # Display the story with separators
                #print("=" * 80 + "\n")
                story_lines = self._wrap_text(new_story, self.term.width - 4)
                for line in story_lines:
                    self.story_engine.typewriter_effect(line.strip(), style=self.text_color)
                #print("\n" + "=" * 80 + "\n")
                
                # Display choices with clean numbering
                print("\nWhat would you like to do?\n")
                for i, choice in enumerate(new_choices, 1):
                    self.story_engine.typewriter_effect(f"{i}. {choice}", delay=0.01, style=self.highlight)
                
                # Display instructions
                print("\n" + self.dim + "Press 1, 2, or 3 to make your choice..." + self.term.normal)
                print(self.dim + "Press Esc to return to reality." + self.term.normal)
                print(self.dim + "Press F9 to save your adventure or F10 to load a saved one." + self.term.normal)
            else:
                # Show error and redisplay current state
                print("\n" + self.error + "The alien device buzzes angrily - even cosmic horrors appreciate valid inputs." + self.term.normal)
                print(self.error + "Failed to generate next story segment. Please try again." + self.term.normal)
                time.sleep(2)
                self.display_story()
        except Exception as e:
            print(f"\n{self.error}Error processing choice: {str(e)}{self.term.normal}")
            time.sleep(2)
            self.display_story()
    
    def bitcoin(self):
        """Check and display current Bitcoin price and changes."""
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
            
            # Add a cosmic message
            cosmic_msg = "The digital currency fluctuates in the cosmic void..."
            msg_x = (self.term.width - len(cosmic_msg)) // 2
            print(self.term.move_xy(msg_x, y + 8) + self.text_color + cosmic_msg + self.term.normal)
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
        """Trigger a panic event."""
        print("PANIC EVENT TRIGGERED")
    
    def stocks(self):
        """Check and display current stock market indices."""
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
            
            # Display each index
            for i, index in enumerate(indices_data):
                symbol = index["symbol"]
                price = index["price"]
                change = index["change"]
                
                # Calculate percentage of change relative to price
                percentage = (change / price) * 100 if price else 0
                percentage_str = f"+{percentage:.2f}%" if percentage >= 0 else f"{percentage:.2f}%"
                
                # Determine color for price changes
                change_color = self.term.green if percentage >= 0 else self.term.red
                
                # Display the index data
                print(self.term.move_xy(x + 2, y + 3 + i * 2) + self.highlight + f"{symbol}: " + self.term.normal + f"${price:,.2f}")
                print(self.term.move_xy(x + 2, y + 4 + i * 2) + self.highlight + f"Change: " + self.term.normal + change_color + percentage_str + self.term.normal)
            
            # Add a cosmic message
            cosmic_msg = "The market indices pulse with cosmic energy..."
            msg_x = (self.term.width - len(cosmic_msg)) // 2
            print(self.term.move_xy(msg_x, y + len(indices_data) * 2 + 4) + self.text_color + cosmic_msg + self.term.normal)
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
        """Check and display current weather data."""
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
            
            # Add a cosmic message
            cosmic_msg = "The weather patterns shift like cosmic tides..."
            msg_x = (self.term.width - len(cosmic_msg)) // 2
            print(self.term.move_xy(msg_x, y + 9) + self.text_color + cosmic_msg + self.term.normal)
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
        # Top border with title
        print(self.term.move_xy(x, y) + "╔" + "═" * (width-2) + "╗")
        if title:
            title_pos = x + (width - len(title)) // 2
            print(self.term.move_xy(title_pos, y) + self.term.bold + f" {title} " + self.term.normal)
            
        # Side borders
        for i in range(y+1, y+height-1):
            print(self.term.move_xy(x, i) + "║" + " " * (width-2) + "║")
            
        # Bottom border
        print(self.term.move_xy(x, y+height-1) + "╚" + "═" * (width-2) + "╝")
    
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
            self.current_saves = self.story_engine.get_save_files()
            
            # Display save menu
            os.system('cls' if os.name == 'nt' else 'clear')
            self.display_save_menu()
            
            # Wait for user selection
            while self.save_menu_active and self.running:
                key = self.term.inkey()
                self.handle_save_menu_key(key)
        else:
            print("\033[33mStory saving is only available in story mode.\033[0m")
    
    def display_save_menu(self):
        """Display the save game menu with a split screen layout"""
        # Clear the screen once
        print(self.term.clear)
        
        # Get terminal dimensions
        terminal_width = self.term.width
        terminal_height = self.term.height
        
        # Calculate split dimensions (left panel takes 1/3, right panel takes 2/3)
        left_width = min(terminal_width // 3, 40)
        right_width = terminal_width - left_width - 3  # 3 chars for separator and spacing
        
        # Prepare header
        header = "=== SAVE REALITY FRAGMENT ==="
        
        # Center the header
        header_pos = (terminal_width - len(header)) // 2
        print(self.term.move_xy(header_pos, 1) + self.term.cyan + header + self.term.normal)
        
        # Instructions at the bottom
        instructions = "Use ↑/↓ to navigate, Enter to select, Esc to cancel"
        instructions_pos = (terminal_width - len(instructions)) // 2
        print(self.term.move_xy(instructions_pos, terminal_height - 2) + 
              self.term.cyan + instructions + self.term.normal)
        
        # Left panel - save list
        left_panel_y = 3
        print(self.term.move_xy(2, left_panel_y) + self.term.underline + 
              "Available Save Slots".ljust(left_width) + self.term.normal)
        
        # Display option to create new save
        left_panel_y += 2
        if self.menu_selection == 0:
            print(self.term.move_xy(2, left_panel_y) + self.term.green + "> Create new save" + self.term.normal)
        else:
            print(self.term.move_xy(2, left_panel_y) + "  Create new save")
        
        # Display existing saves that can be overwritten
        for i, save in enumerate(self.current_saves, 1):
            timestamp = save.get('timestamp', 'Unknown')
            if isinstance(timestamp, str) and timestamp != 'Unknown':
                try:
                    # Try to parse ISO format timestamp
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime("%Y-%m-%d %H:%M")
                except (ValueError, TypeError):
                    # Keep original if parsing fails
                    pass
            
            title = save.get('title', 'Untitled save')
            
            # Truncate title if too long
            if len(title) > left_width - 5:
                title = title[:left_width - 8] + "..."
            
            left_panel_y += 2
            if i == self.menu_selection:
                print(self.term.move_xy(2, left_panel_y) + self.term.green + 
                      f"> {i}. {title}" + self.term.normal)
                print(self.term.move_xy(5, left_panel_y + 1) + self.term.green + 
                      f"({timestamp})" + self.term.normal)
            else:
                print(self.term.move_xy(2, left_panel_y) + 
                      f"  {i}. {title}")
                print(self.term.move_xy(5, left_panel_y + 1) + 
                      f"({timestamp})")
        
        # Draw a vertical line to separate panels
        for y in range(3, terminal_height - 3):
            print(self.term.move_xy(left_width + 2, y) + "│")
        
        # Right panel - Preview/Summary
        right_panel_x = left_width + 4
        right_panel_y = 3
        
        print(self.term.move_xy(right_panel_x, right_panel_y) + self.term.underline + 
              "Story Preview".ljust(right_width) + self.term.normal)
        
        right_panel_y += 2
        
        # Show preview of the selected save or current story
        preview_text = ""
        
        if self.menu_selection == 0 or not self.current_saves:
            # For new save, show the current story
            preview_text = "New Save - Current Story:"
            right_panel_y += 1
            print(self.term.move_xy(right_panel_x, right_panel_y) + self.term.bold + preview_text + self.term.normal)
            
            # Get the last few lines of the current story
            story_preview = self.story_engine.current_story
            # Limit to last 300 chars to fit in the panel
            if len(story_preview) > 300:
                story_preview = "..." + story_preview[-300:]
            
            # Wrap text to fit the right panel
            right_panel_y += 1
            for line in self._wrap_text(story_preview, right_width):
                print(self.term.move_xy(right_panel_x, right_panel_y) + line)
                right_panel_y += 1
                if right_panel_y >= terminal_height - 6:  # Leave room for choices
                    break
            
            # Display current choices
            if self.story_engine.current_choices:
                right_panel_y += 1
                print(self.term.move_xy(right_panel_x, right_panel_y) + self.term.bold + "Current Choices:" + self.term.normal)
                right_panel_y += 1
                
                for i, choice in enumerate(self.story_engine.current_choices, 1):
                    # Truncate choice if too long
                    if len(choice) > right_width - 5:
                        choice = choice[:right_width - 8] + "..."
                    
                    print(self.term.move_xy(right_panel_x, right_panel_y) + f"{i}. {choice}")
                    right_panel_y += 1
                    if right_panel_y >= terminal_height - 3:
                        break
        else:
            # Show preview of the selected save
            selected_save = self.current_saves[self.menu_selection - 1]
            preview_text = f"Save Preview: {selected_save.get('title', 'Untitled')}"
            right_panel_y += 1
            print(self.term.move_xy(right_panel_x, right_panel_y) + self.term.bold + preview_text + self.term.normal)
            
            # Get the story summary from the save
            story_summary = selected_save.get('summary', 'No preview available')
            
            # Wrap text to fit the right panel
            right_panel_y += 1
            summary_lines = 0
            for line in self._wrap_text(story_summary, right_width):
                print(self.term.move_xy(right_panel_x, right_panel_y) + line)
                right_panel_y += 1
                summary_lines += 1
                if right_panel_y >= terminal_height - 6:  # Leave room for choices
                    break
            
            # Display choices from the save if available
            choices_preview = selected_save.get('choices_preview', '')
            if choices_preview and summary_lines < terminal_height - 10:
                # Extract choices from the choices_preview text
                choices = []
                for line in choices_preview.split('\n'):
                    if line.startswith('- '):
                        choices.append(line[2:])  # Remove the "- " prefix
                
                if choices:
                    right_panel_y += 1
                    print(self.term.move_xy(right_panel_x, right_panel_y) + self.term.bold + "Choices at Save Point:" + self.term.normal)
                    right_panel_y += 1
                    
                    for i, choice in enumerate(choices, 1):
                        # Truncate choice if too long
                        if len(choice) > right_width - 5:
                            choice = choice[:right_width - 8] + "..."
                        
                        print(self.term.move_xy(right_panel_x, right_panel_y) + f"{i}. {choice}")
                        right_panel_y += 1
                        if right_panel_y >= terminal_height - 3:
                            break
    
    def _wrap_text(self, text, width):
        """Wrap text to fit within a specified width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Check if adding this word would exceed the width
            if current_line and len(' '.join(current_line + [word])) > width:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        
        # Add the last line if it's not empty
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def handle_save_menu_key(self, key):
        """Handle key presses in the save menu"""
        max_selection = len(self.current_saves)
        redraw = False
        
        if key.name == 'KEY_UP':
            self.menu_selection = (self.menu_selection - 1) % (max_selection + 1)
            redraw = True
        elif key.name == 'KEY_DOWN':
            self.menu_selection = (self.menu_selection + 1) % (max_selection + 1)
            redraw = True
        elif key.name == 'KEY_ESCAPE':
            # Exit the save menu
            self.save_menu_active = False
            
            # Redisplay the story
            self.display_story()
        elif key.name == 'KEY_ENTER':
            if self.menu_selection == 0:  # New save
                # Generate a new save ID
                save_id = self.story_engine.generate_save_id()
                # Generate a default title based on timestamp
                title = f"Reality Glitch - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                # Save the game
                if self.story_engine.save_story(save_id=save_id, title=title):
                    # Exit the menu
                    self.save_menu_active = False
                    # Show success message
                    print(self.term.clear)
                    print("\n" + self.text_color + "Successfully saved reality fragment." + self.term.normal)
                    time.sleep(1)
                    # Redisplay the story
                    self.display_story()
                else:
                    # Show error and wait for acknowledgement
                    print("\n" + self.error + "Failed to save reality fragment." + self.term.normal)
                    print("Press any key to continue...")
                    self.term.inkey()
                    # Redisplay the save menu
                    self.display_save_menu()
            else:
                # Use an existing save
                save_id = self.current_saves[self.menu_selection - 1]['id']
                title = self.current_saves[self.menu_selection - 1]['title']
                # Save the game
                if self.story_engine.save_story(save_id=save_id, title=title):
                    # Exit the menu
                    self.save_menu_active = False
                    # Show success message
                    print(self.term.clear)
                    print("\n" + self.text_color + "Successfully updated reality fragment." + self.term.normal)
                    time.sleep(1)
                    # Redisplay the story
                    self.display_story()
                else:
                    # Show error and wait for acknowledgement
                    print("\n" + self.error + "Failed to update reality fragment." + self.term.normal)
                    print("Press any key to continue...")
                    self.term.inkey()
                    # Redisplay the save menu
                    self.display_save_menu()
        
        # Only redraw if needed
        if redraw:
            self.display_save_menu()
    
    def load_story(self):
        """Load a saved story with menu for selecting save slot"""
        # Check if there are any saves
        if not self.story_engine.has_saved_story():
            print("\033[33mNo saved stories found in the cosmic archives.\033[0m")
            return
        
        # Set the load menu to active
        self.load_menu_active = True
        self.menu_selection = 0
        
        # Get existing saves
        self.current_saves = self.story_engine.get_save_files()
        
        # Display load menu
        os.system('cls' if os.name == 'nt' else 'clear')
        self.display_load_menu()
        
        # Wait for user selection
        while self.load_menu_active and self.running:
            key = self.term.inkey()
            self.handle_load_menu_key(key)
    
    def display_load_menu(self):
        """Display the load game menu with a split screen layout"""
        # Clear the screen once
        print(self.term.clear)
        
        # Get terminal dimensions
        terminal_width = self.term.width
        terminal_height = self.term.height
        
        # Calculate split dimensions (left panel takes 1/3, right panel takes 2/3)
        left_width = min(terminal_width // 3, 40)
        right_width = terminal_width - left_width - 3  # 3 chars for separator and spacing
        
        # Prepare header
        header = "=== LOAD REALITY FRAGMENT ==="
        
        # Center the header
        header_pos = (terminal_width - len(header)) // 2
        print(self.term.move_xy(header_pos, 1) + self.term.cyan + header + self.term.normal)
        
        # Instructions at the bottom
        if self.current_saves:
            instructions = "Use ↑/↓ to navigate, Enter to select, Esc to cancel"
            instructions_pos = (terminal_width - len(instructions)) // 2
            print(self.term.move_xy(instructions_pos, terminal_height - 2) + 
                  self.term.cyan + instructions + self.term.normal)
        
        # Left panel - save list
        left_panel_y = 3
        print(self.term.move_xy(2, left_panel_y) + self.term.underline + 
              "Saved Reality Fragments".ljust(left_width) + self.term.normal)
        
        # Display available saves
        if not self.current_saves:
            left_panel_y += 2
            print(self.term.move_xy(2, left_panel_y) + self.term.yellow + 
                  "No saved games found." + self.term.normal)
            print(self.term.move_xy(2, left_panel_y + 2) + 
                  "Press Esc to return.")
        else:
            for i, save in enumerate(self.current_saves):
                timestamp = save.get('timestamp', 'Unknown')
                if isinstance(timestamp, str) and timestamp != 'Unknown':
                    try:
                        # Try to parse ISO format timestamp
                        dt = datetime.fromisoformat(timestamp)
                        timestamp = dt.strftime("%Y-%m-%d %H:%M")
                    except (ValueError, TypeError):
                        # Keep original if parsing fails
                        pass
                
                title = save.get('title', 'Untitled save')
                
                # Truncate title if too long
                if len(title) > left_width - 5:
                    title = title[:left_width - 8] + "..."
                
                left_panel_y += 2
                if i == self.menu_selection:
                    print(self.term.move_xy(2, left_panel_y) + self.term.green + 
                          f"> {i+1}. {title}" + self.term.normal)
                    print(self.term.move_xy(5, left_panel_y + 1) + self.term.green + 
                          f"({timestamp})" + self.term.normal)
                else:
                    print(self.term.move_xy(2, left_panel_y) + 
                          f"  {i+1}. {title}")
                    print(self.term.move_xy(5, left_panel_y + 1) + 
                          f"({timestamp})")
        
        # Draw a vertical line to separate panels
        for y in range(3, terminal_height - 3):
            print(self.term.move_xy(left_width + 2, y) + "│")
        
        # Right panel - Preview/Summary
        if self.current_saves:
            right_panel_x = left_width + 4
            right_panel_y = 3
            
            print(self.term.move_xy(right_panel_x, right_panel_y) + self.term.underline + 
                  "Story Preview".ljust(right_width) + self.term.normal)
            
            right_panel_y += 2
            
            # Show preview of the selected save
            selected_save = self.current_saves[self.menu_selection]
            preview_text = f"Fragment: {selected_save.get('title', 'Untitled')}"
            print(self.term.move_xy(right_panel_x, right_panel_y) + self.term.bold + preview_text + self.term.normal)
            
            # Get the story summary from the save
            story_summary = selected_save.get('summary', 'No preview available')
            
            # Wrap text to fit the right panel
            right_panel_y += 2
            summary_lines = 0
            for line in self._wrap_text(story_summary, right_width):
                print(self.term.move_xy(right_panel_x, right_panel_y) + line)
                right_panel_y += 1
                summary_lines += 1
                if right_panel_y >= terminal_height - 6:  # Leave room for choices
                    break
            
            # Display choices from the save if available
            choices_preview = selected_save.get('choices_preview', '')
            if choices_preview and summary_lines < terminal_height - 10:
                # Extract choices from the choices_preview text
                choices = []
                for line in choices_preview.split('\n'):
                    if line.startswith('- '):
                        choices.append(line[2:])  # Remove the "- " prefix
                
                if choices:
                    right_panel_y += 1
                    print(self.term.move_xy(right_panel_x, right_panel_y) + self.term.bold + "Choices at Save Point:" + self.term.normal)
                    right_panel_y += 1
                    
                    for i, choice in enumerate(choices, 1):
                        # Truncate choice if too long
                        if len(choice) > right_width - 5:
                            choice = choice[:right_width - 8] + "..."
                        
                        print(self.term.move_xy(right_panel_x, right_panel_y) + f"{i}. {choice}")
                        right_panel_y += 1
                        if right_panel_y >= terminal_height - 3:
                            break
    
    def handle_load_menu_key(self, key):
        """Handle key presses in the load menu"""
        if not self.current_saves:
            if key.name == 'KEY_ESCAPE':
                self.load_menu_active = False
                # Clear the blessed terminal screen
                print(self.term.clear + self.term.home)
                # If in story mode, redisplay the story
                if self.story_mode:
                    self.display_story()
                else:
                    self.display_welcome()
            return
        
        redraw = False
        max_selection = len(self.current_saves) - 1
        
        if key.name == 'KEY_UP':
            self.menu_selection = (self.menu_selection - 1) % (max_selection + 1)
            redraw = True
        elif key.name == 'KEY_DOWN':
            self.menu_selection = (self.menu_selection + 1) % (max_selection + 1)
            redraw = True
        elif key.name == 'KEY_ESCAPE':
            # Exit the load menu
            self.load_menu_active = False
            
            # Clear the blessed terminal screen
            print(self.term.clear + self.term.home)
            
            # If in story mode, redisplay the story
            if self.story_mode:
                self.display_story()
            else:
                self.display_welcome()
        elif key.name == 'KEY_ENTER':
            # Process the selection
            save_id = self.current_saves[self.menu_selection]['id']
            
            # Create a status message at the bottom of the screen
            message_y = self.term.height - 4
            message_x = (self.term.width - 50) // 2
            print(self.term.move_xy(message_x, message_y) + 
                  "A familiar cosmic shimmer appears as your saved story materializes...")
            
            if self.story_engine.load_story(save_id=save_id):
                # Set flag to prevent reset when entering story mode
                self.loaded_from_save = True
                # Enter story mode
                if not self.story_mode:
                    self.story_mode = True
                
                # Exit the load menu
                self.load_menu_active = False
                
                # Display the loaded story using the proper method
                self.display_story()
            else:
                print(self.term.move_xy(message_x, message_y) + 
                      self.term.red + "The cosmic archives appear to be damaged. Failed to load story." + self.term.normal)
                print(self.term.move_xy(message_x, message_y + 1) + 
                      "Press any key to continue...")
                self.term.inkey()
                self.load_menu_active = False
                if self.story_mode:
                    # Redisplay the current story
                    self.display_story()
                else:
                    self.display_welcome()
        
        # Only redraw if needed
        if redraw:
            self.display_load_menu()
    
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
    
    def show_save_list(self):
        """Show a list of all saved games"""
        saves = self.story_engine.get_save_files()
        
        print("\n=== SAVED REALITY FRAGMENTS ===")
        if not saves:
            print("\033[33mNo saved games found in the cosmic archives.\033[0m")
            return
        
        for i, save in enumerate(saves, 1):
            timestamp = save.get('timestamp', 'Unknown')
            if isinstance(timestamp, str) and timestamp != 'Unknown':
                try:
                    # Try to parse ISO format timestamp
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime("%Y-%m-%d %H:%M")
                except (ValueError, TypeError):
                    # Keep original if parsing fails
                    pass
            
            title = save.get('title', 'Untitled save')
            summary = save.get('summary', 'No summary available')
            
            print(f"\n{i}. {title}")
            print(f"   Saved: {timestamp}")
            print(f"   {summary}")
        

        print(f"\nSave location: {os.path.abspath(SAVE_DIR)}")
    
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
        elif key.name == 'KEY_F8':
            self.show_save_list()
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
                # Wait for a keypress
                key = self.term.inkey()
                
                # Debug output for key presses
                if self.story_mode:
                    print(f"\nDebug - Key pressed: '{key}', Key name: '{key.name}', is_sequence: {key.is_sequence}")
                
                if self.save_menu_active:
                    # Handle save menu keys
                    self.handle_save_menu_key(key)
                    
                elif self.load_menu_active:
                    # Handle load menu keys
                    self.handle_load_menu_key(key)
                    
                elif self.story_mode:
                    # Handle story mode keys
                    if key.name == 'KEY_ESCAPE':
                        self.story_mode = False
                        self.display_welcome()
                    elif key.name == 'KEY_F9':
                        self.save_story()
                    elif key.name == 'KEY_F10':
                        self.load_story()
                    elif key.name == 'KEY_F8':
                        self.show_save_list()
                        # Wait for any key to continue
                        print("\nPress any key to continue...")
                        self.term.inkey()
                        # Redisplay story
                        self.display_story()
                    elif key.name == 'KEY_F7':
                        self.show_save_location()
                        # Wait for any key to continue
                        print("\nPress any key to continue...")
                        self.term.inkey()
                        # Redisplay story
                        self.display_story()
                    # Handle choice keys - check BOTH key.name and key itself
                    elif key.name in ['KEY_1', 'KEY_2', 'KEY_3']:
                        self.handle_story_choice(key)
                    elif key == '1' or key == '2' or key == '3': 
                        # Create a mock key object with a name property for numeric keys
                        class MockKey:
                            def __init__(self, name):
                                self.name = name
                        
                        # Map the key to the corresponding KEY_ name
                        key_name = 'KEY_' + key
                        mock_key = MockKey(key_name)
                        print(f"\nDebug - Using numeric key '{key}', created mock key with name: '{mock_key.name}'")
                        self.handle_story_choice(mock_key)
                    elif key.name == 'KEY_F1':
                        self.display_help()
                        # Wait for any key to continue
                        print("\nPress any key to continue...")
                        self.term.inkey()
                        # Redisplay story
                        self.display_story()
                    # Explicitly handle other function keys to prevent falling through
                    elif key.name in ['KEY_F2', 'KEY_F3', 'KEY_F4', 'KEY_F5', 'KEY_F6']:
                        # Display a message about these not being available in story mode
                        print("\n" + self.warning + "This command is not available in story mode." + self.term.normal)
                        time.sleep(1.5)
                        # Redisplay story
                        self.display_story()
                    else:
                        print(f"\n{self.warning}Unrecognized key: '{key}', key.name: '{key.name}'{self.term.normal}")
                        time.sleep(1)
                        self.display_story()
                else:
                    # Reality mode - handle regular commands
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