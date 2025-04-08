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
import random
from integration.reality_data import RealityData

class RealityGlitchGame:        
    def __init__(self):
        """Initialize the game and its components."""
        self.db_ops = DatabaseOperations()
        self.running = True
        self.term = blessed.Terminal()
        self.story_mode = False
        self.story_engine = StoryEngine(debug=False)
        self.loaded_from_save = False
        self.save_menu_active = False
        self.load_menu_active = False
        self.current_saves = []
        self.menu_selection = 0
        
        # Reality data handler for reality glitches
        self.reality_data = RealityData(debug=False)
        
        # Simplified color scheme inspired by terminal aesthetics
        self.text_color = self.term.teal  # Main text color
        self.highlight = self.term.white  # For emphasis
        self.dim = self.term.dim  # For less important text
        self.warning = self.term.yellow  # For warnings/important info
        self.error = self.term.red  # For errors
        
        # Check if this is the first run and sync with APIs if needed
        if self.db_ops.is_first_run():
            # Silently sync with APIs on first run (no messages to terminal)
            sync = SyncApis()
            sync.sync_all()
        else:
            # Check if we need to sync on startup (silent)
            self.check_and_sync()
    
    def check_and_sync(self):
        """Check if 10 minutes have passed since last sync and sync if needed - silently."""
        last_sync = self.db_ops.get_last_sync_time()           
        if not last_sync or (datetime.now() - last_sync) > timedelta(minutes=10):        
            # No console output - run sync silently
            sync = SyncApis()
            sync.sync_all()
    
    def display_welcome(self):
        """Display the welcome message with clean terminal aesthetics."""
        # Clear screen
        print(self.term.clear)
                
        title_art = """
██████╗ ███████╗ █████╗ ██╗     ██╗████████╗██╗   ██╗     ██████╗ ██╗     ██║████████╗ ██████╗██╗  ██╗
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
        instructions = ["Press F1 for help. Press Esc to exit.", "Press F10 to load a saved story."]
        for i, line in enumerate(instructions):
            instr_x = (self.term.width - len(line)) // 2
            print(self.term.move_xy(instr_x, y+3+i) + self.dim + line + self.term.normal)
    
    def display_help(self):
        """Display help information."""
        # Clear screen
        print(self.term.clear)
        
        # Print help header
        print(self.term.bold + self.term.yellow + "\n REALITY GLITCH - HELP INFORMATION" + self.term.normal)
        print("\n" + self.term.dim + " A cosmic horror adventure with tendrils in the real world" + self.term.normal)
        
        print("\n" + self.term.bold + " KEY COMMANDS:" + self.term.normal)
        print("\n " + self.term.bold + "F1: " + self.term.normal + "Display this help")
        print(" " + self.term.bold + "F2: " + self.term.normal + "Check Bitcoin status")
        print(" " + self.term.bold + "F3: " + self.term.normal + "Check stock market")
        print(" " + self.term.bold + "F4: " + self.term.normal + "Check weather conditions")
        print(" " + self.term.bold + "F5: " + self.term.normal + "Trigger system alert (DEBUG)")
        print(" " + self.term.bold + "F6: " + self.term.normal + "Toggle story mode")
        print(" " + self.term.bold + "F7: " + self.term.normal + "Display quantum animation")
        print(" " + self.term.bold + "F9: " + self.term.normal + "Save story (in story mode)")
        print(" " + self.term.bold + "F10: " + self.term.normal + "Load story (in story mode)")
        print(" " + self.term.bold + "ESC: " + self.term.normal + "Exit the simulation")
        
        print("\n" + self.term.bold + " STORY MODE:" + self.term.normal)
        print(" In story mode, use number keys 1-3 to make choices.")
        print(" The story adapts based on real-world data.")
        
        print("\n" + self.term.bold + " REALITY GLITCHES:" + self.term.normal)
        print(" This program integrates real-world data to create 'reality glitches'")
        print(" in the narrative. Events like Bitcoin price changes, weather conditions,")
        print(" and stock market fluctuations affect the story's tone and events.")
        
        print("\n" + self.term.bold + " DATA SOURCES:" + self.term.normal)
        print(" - Cryptocurrency prices")
        print(" - Stock market indices")
        print(" - Local weather conditions")
        
        # Add warning about the nature of the simulation
        print("\n" + self.term.red + " WARNING: " + self.term.normal + "Extended use may cause questioning of reality itself.")
        print(" " + self.term.dim + "This is a work of fiction. Any correlation with actual ")
        print(" existential threats is purely coincidental." + self.term.normal)
        
        # Wait for key press
        print("\nPress any key to return...")
        self.term.inkey()
    
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
        # Skip if typewriter animation is active
        if self.story_engine.typewriter_active:
            return
            
        try:
            choice_index = -1
            # Use normalized_name if available, otherwise use name
            key_name = getattr(key, 'normalized_name', key.name)
            
            # Check for various ways the number keys can be represented
            if key_name == 'KEY_1' or key_name == 'KEY_2' or key_name == 'KEY_3':
                # Numpad or function key format
                choice_index = int(key_name[-1]) - 1
            elif key == '1' or key == '2' or key == '3':
                # Direct string representation of the key
                choice_index = int(key) - 1
            elif hasattr(key, 'code') and key.code in [49, 50, 51]:
                # ASCII codes for 1, 2, 3
                choice_index = key.code - 49
            elif isinstance(key, str) and key.isdigit() and 1 <= int(key) <= 3:
                # String digit
                choice_index = int(key) - 1
            elif key_name == 'KEY_ESCAPE':
                self.story_mode = False
                self.display_welcome()
                return
            
            # Validate choice index
            if choice_index < 0 or choice_index >= len(self.story_engine.current_choices):
                print("\n" + self.error + "Invalid choice number. Please try again." + self.term.normal)
                time.sleep(1)
                self.display_story()
                return
                
            # Process the valid choice
            print(f"\nProcessing choice {choice_index+1}...")
            
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
                # Display the new story state using the enhanced UI
                self.display_story()
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
        # Clear screen
        print(self.term.clear)
        
        # Title
        title = "REALITY PANIC EVENT"
        title_x = (self.term.width - len(title)) // 2
        print(self.term.move_xy(title_x, 2) + self.error + title + self.term.normal)
        
        # Refresh the reality data to get the latest state
        self.reality_data.refresh_data()
        
        # Generate intensified reality glitches
        glitches = self.reality_data.get_reality_glitches()
        combined = glitches["combined"]
        
        # Setting for intense glitches
        intense_anomalies = []
        
        # Add all available anomalies from all data sources
        for source in ["bitcoin", "weather", "stocks"]:
            if glitches[source]["active"]:
                intense_anomalies.extend(glitches[source]["events"])
        
        # If we have no anomalies, generate some fallbacks
        if not intense_anomalies:
            intense_anomalies = [
                "The screens around you display impossible coordinates",
                "Your shadow moves independently of your body",
                "Time seems to slow down and speed up randomly",
                "Reflections show alternate versions of yourself",
                "Languages temporarily become incomprehensible",
                "Objects momentarily lose their solidity",
                "The air tastes like static electricity",
                "Sounds echo before they're made",
                "Your memories feel like they belong to someone else",
                "Gravity shifts direction unpredictably"
            ]
        
        # Select random anomalies for the panic event
        display_anomalies = random.sample(
            intense_anomalies,
            min(5, len(intense_anomalies))
        )
        
        # Display the anomalies with visual effects
        print(self.term.move_xy((self.term.width - 50) // 2, 4) + 
              self.warning + "MULTIPLE REALITY GLITCHES DETECTED" + self.term.normal)
        
        y = 6
        for anomaly in display_anomalies:
            # Random position with jitter effect
            x = random.randint(10, self.term.width - len(anomaly) - 10)
            
            # Random style for each anomaly
            styles = [self.text_color, self.highlight, self.warning, self.error]
            style = random.choice(styles)
            
            # Display with slight delay
            print(self.term.move_xy(x, y) + style + anomaly + self.term.normal)
            y += 2
            time.sleep(0.3)
        
        # Display visual effects simulating reality breaking down
        for i in range(3):
            # Flash effect
            print(self.term.clear)
            time.sleep(0.1)
            
            # Display glitch pattern
            for j in range(5):
                x = random.randint(0, self.term.width - 10)
                y = random.randint(0, self.term.height - 2)
                glitch_chars = random.choice(["░░░", "▒▒▒", "▓▓▓", "███", "///", "\\\\\\"])
                print(self.term.move_xy(x, y) + self.error + glitch_chars + self.term.normal)
            
            time.sleep(0.2)
        
        # Return to normal display
        print(self.term.clear)
        
        # Show aftermath message
        aftermsg = "Reality stabilizing... glitches contained... for now..."
        msg_x = (self.term.width - len(aftermsg)) // 2
        print(self.term.move_xy(msg_x, (self.term.height - 4) // 2) + 
              self.warning + aftermsg + self.term.normal)
        
        # Effect on story generation if in story mode
        if self.story_mode:
            notice = "The story will be affected by these reality anomalies"
            notice_x = (self.term.width - len(notice)) // 2
            print(self.term.move_xy(notice_x, (self.term.height - 4) // 2 + 2) + 
                  self.text_color + notice + self.term.normal)
        
        # Footer
        footer = "Press any key to continue..."
        footer_x = (self.term.width - len(footer)) // 2
        print(self.term.move_xy(footer_x, self.term.height - 2) + 
              self.dim + footer + self.term.normal)
        
        # Wait for key press
        self.term.inkey()
        
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
        
        # Use normalized_name if available, otherwise use name
        key_name = getattr(key, 'normalized_name', key.name)
        
        if key_name == 'KEY_UP':
            self.menu_selection = (self.menu_selection - 1) % (max_selection + 1)
            redraw = True
        elif key_name == 'KEY_DOWN':
            self.menu_selection = (self.menu_selection + 1) % (max_selection + 1)
            redraw = True
        elif key_name == 'KEY_ESCAPE':
            # Exit the save menu
            self.save_menu_active = False
            
            # Redisplay the story
            self.display_story()
        elif key_name == 'KEY_ENTER':
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
            # Use normalized_name if available, otherwise use name
            key_name = getattr(key, 'normalized_name', key.name)
            
            if key_name == 'KEY_ESCAPE':
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
        
        # Use normalized_name if available, otherwise use name
        key_name = getattr(key, 'normalized_name', key.name)
        
        if key_name == 'KEY_UP':
            self.menu_selection = (self.menu_selection - 1) % (max_selection + 1)
            redraw = True
        elif key_name == 'KEY_DOWN':
            self.menu_selection = (self.menu_selection + 1) % (max_selection + 1)
            redraw = True
        elif key_name == 'KEY_ESCAPE':
            # Exit the load menu
            self.load_menu_active = False
            
            # Clear the blessed terminal screen
            print(self.term.clear + self.term.home)
            
            # If in story mode, redisplay the story
            if self.story_mode:
                self.display_story()
            else:
                self.display_welcome()
        elif key_name == 'KEY_ENTER':
            # Process the selection
            save_id = self.current_saves[self.menu_selection]['id']
            
            # Create a status message at the bottom of the screen
            message_y = self.term.height - 4
            message_x = (self.term.width - 50) // 2
            
            print(self.term.move_xy(message_x, message_y) + 
                  "A familiar cosmic shimmer appears as your saved story materializes...")
            
            # Exit the load menu before loading the story to avoid UI conflicts
            self.load_menu_active = False
            
            # Clear screen before loading
            print(self.term.clear)
            
            # Load the save file
            if self.story_engine.load_story(save_id=save_id):
                # Set flag to prevent reset when entering story mode
                self.loaded_from_save = True
                # Enter story mode
                if not self.story_mode:
                    self.story_mode = True
                
                # Display the story with a short delay to ensure UI is properly rendered
                time.sleep(0.5)
                # Force a redraw of the story screen
                print(self.term.clear)
                self.display_story()
            else:
                print(self.term.move_xy(message_x, message_y) + 
                      self.term.red + "The cosmic archives appear to be damaged. Failed to load story." + self.term.normal)
                print(self.term.move_xy(message_x, message_y + 1) + 
                      "Press any key to continue...")
                self.term.inkey()
                
                if self.story_mode:
                    # Redisplay the current story
                    self.display_story()
                else:
                    self.display_welcome()
        
        # Only redraw if needed
        if redraw:
            self.display_load_menu()
    
    def show_save_location(self):
        """Show the location where save files are stored."""
        save_path = os.path.abspath(self.story_engine.SAVE_DIR)
        print(f"\nSave files are stored in: {save_path}")
        
        # Print some tips
        print(self.dim + "\nTip: These files can be backed up manually if desired." + self.term.normal)
        print(self.dim + "     Do not modify save files manually - this may corrupt them." + self.term.normal)
    
    def handle_key(self, key):
        """Handle key presses."""
        # Ignore keyboard input if typewriter animation is active
        if self.story_engine.typewriter_active:
            return
            
        if self.save_menu_active:
            self.handle_save_menu_key(key)
            return
        elif self.load_menu_active:
            self.handle_load_menu_key(key)
            return
        
        # Normalize function key names to consistent format
        key_name = key.name
        if key_name and key_name.startswith('KEY_F') and not key_name.startswith('KEY_F('):
            # Convert KEY_F1 to KEY_F(1)
            num = key_name[5:]
            key_name = f'KEY_F({num})'
        
        # Keep a reference to the original key but use normalized name
        key.normalized_name = key_name
        
        if self.story_mode:
            # F-keys still work in story mode
            if key_name == 'KEY_F(1)':
                self.display_help()
            elif key_name == 'KEY_F(7)':
                self.display_sci_fi_animation()
            elif key_name == 'KEY_F(9)':
                self.save_story()
            elif key_name == 'KEY_F(10)':
                self.load_story()
            else:
                self.handle_story_choice(key)
        else:
            # Handle main menu keys
            if key_name == 'KEY_F(1)':
                self.display_help()
            elif key_name == 'KEY_F(2)':
                self.bitcoin()
            elif key_name == 'KEY_F(3)':
                self.stocks()
            elif key_name == 'KEY_F(4)':
                self.weather()
            elif key_name == 'KEY_F(5)':
                self.trigger_panic()
            elif key_name == 'KEY_F(6)':
                self.toggle_story_mode()
            elif key_name == 'KEY_F(7)':
                self.display_sci_fi_animation()
            elif key_name == 'KEY_F(9)' and self.story_engine.has_saved_story():
                self.save_story()
            elif key_name == 'KEY_F(10)' and self.story_engine.has_saved_story():
                self.load_story()
            elif key_name == 'KEY_ESCAPE':
                self.running = False
    
    def display_sci_fi_animation(self, duration=5):
        """Display an immersive sci-fi loading animation"""
        # Clear screen and hide cursor
        print(self.term.clear)
        print(self.term.hide_cursor)
        
        # Define animation variables
        frames = ["◢◣", "◣◥", "◥◤", "◤◢"]
        colors = [self.text_color, self.highlight, self.warning, self.term.blue, self.term.magenta]
        
        # Set the only message to match the image
        message = "Calibrating quantum entanglement matrix..."
        
        # Matrix effect elements - specifically the Japanese characters shown in the image
        matrix_chars = "デテトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモヤユヨラリルレロワヲンゴザジズゼゾタダチヂッツヅテデト"
        glitch_chars = "█▓▒░█▓▒░"
        
        # Display header
        print("\n\n")
        title = "REALITY SYNCHRONIZATION PROTOCOL"
        title_x = (self.term.width - len(title)) // 2
        print(self.term.move_xy(title_x, 2) + self.highlight + self.term.bold + title + self.term.normal)
        
        # Box dimensions
        width = 70
        height = 15
        start_x = (self.term.width - width) // 2
        start_y = 4
        
        # Draw box
        self.draw_box(start_x, start_y, width, height)
        
        # Start time tracking
        start_time = time.time()
        end_time = start_time + duration
        
        # Animation variables
        i = 0
        
        # Run the animation until duration is reached
        while time.time() < end_time:
            # Update frame 
            frame = frames[i % len(frames)]
            color = colors[i % len(colors)]
            
            # Display the message - only "Calibrating quantum entanglement matrix..."
            msg_x = start_x + 4
            msg_y = start_y + 3
            print(self.term.move_xy(msg_x, msg_y) + " " * (width - 8))  # Clear the line
            print(self.term.move_xy(msg_x, msg_y) + self.term.yellow + frame + " " + message + self.term.normal)
            
            # Create a grid of Japanese characters similar to the image
            # This arranges them in a specific pattern rather than random falling characters
            for row in range(5):
                for col in range(width - 8):
                    if random.random() < 0.05:  # Occasionally update characters
                        char_x = start_x + 4 + col
                        char_y = start_y + 5 + row
                        char = random.choice(matrix_chars)
                        
                        # Style based on position - matching image pattern
                        if row < 2:
                            style = self.term.normal
                        else:
                            style = self.dim
                        
                        print(self.term.move_xy(char_x, char_y) + style + char + self.term.normal)
            
            # Add specific glitch effects at locations similar to the image
            if i % 5 == 0:  # Control the rate of glitch updates
                # First glitch block (left side)
                glitch_x1 = start_x + 10
                glitch_y1 = start_y + 8
                glitch_text1 = ''.join(random.choice(glitch_chars) for _ in range(6))
                print(self.term.move_xy(glitch_x1, glitch_y1) + self.term.magenta + glitch_text1 + self.term.normal)
                
                # Second glitch block (middle bottom)
                glitch_x2 = start_x + 35
                glitch_y2 = start_y + 12
                glitch_text2 = ''.join(random.choice(glitch_chars) for _ in range(8))
                print(self.term.move_xy(glitch_x2, glitch_y2) + self.term.magenta + glitch_text2 + self.term.normal)
                
                # Third glitch block (right side)
                glitch_x3 = start_x + 55
                glitch_y3 = start_y + 7
                glitch_text3 = ''.join(random.choice(glitch_chars) for _ in range(6))
                print(self.term.move_xy(glitch_x3, glitch_y3) + self.term.magenta + glitch_text3 + self.term.normal)
            
            # Show progress bar at bottom of box
            progress = (time.time() - start_time) / duration
            bar_width = width - 8
            filled = int(bar_width * progress)
            bar_x = start_x + 4
            bar_y = start_y + height - 3
            print(self.term.move_xy(bar_x, bar_y) + 
                  self.text_color + "[" + 
                  "=" * filled + 
                  " " * (bar_width - filled) + 
                  "]" +
                  self.term.normal)
            
            # Increment counters
            i += 1
            
            # Sleep for a frame
            time.sleep(0.1)
        
        # Restore cursor and clear screen
        print(self.term.normal_cursor)
        print(self.term.clear)
        
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
                    
                # Skip processing if typewriter animation is active
                if self.story_engine.typewriter_active:
                    # Just discard the key and continue
                    continue
                
                # Add debug output if story_engine is in debug mode
                if self.story_engine.debug:
                    print(f"\nKey: {repr(key)}, Name: {key.name}, Code: {ord(key) if len(key) == 1 else None}")
                
                # Normalize function key names to consistent format
                key_name = key.name
                if key_name and key_name.startswith('KEY_F') and not key_name.startswith('KEY_F('):
                    # Convert KEY_F1 to KEY_F(1)
                    num = key_name[5:]
                    key_name = f'KEY_F({num})'
                    
                    # Show debug info about normalization
                    if self.story_engine.debug:
                        print(f"Normalized key name from {key.name} to {key_name}")
                
                # Keep a reference to the original key but use normalized name
                key.normalized_name = key_name
                
                if self.save_menu_active:
                    # Handle save menu keys
                    self.handle_save_menu_key(key)
                    
                elif self.load_menu_active:
                    # Handle load menu keys
                    self.handle_load_menu_key(key)
                    
                elif self.story_mode:
                    # Handle story mode keys
                    if key_name == 'KEY_ESCAPE':
                        self.story_mode = False
                        self.display_welcome()
                    elif key_name == 'KEY_F(7)':
                        self.display_sci_fi_animation()
                    elif key_name == 'KEY_F(9)':
                        self.save_story()
                    elif key_name == 'KEY_F(10)':
                        self.load_story()
                    else:
                        self.handle_story_choice(key)
                else:
                    # Reality mode - handle regular commands
                    self.handle_key(key)

def start_game_cli(debug=False):
    """Entry point for the game."""
    try:
        game = RealityGlitchGame()
        # Update the story engine to use debug mode if needed
        game.story_engine = StoryEngine(debug=debug)
        
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