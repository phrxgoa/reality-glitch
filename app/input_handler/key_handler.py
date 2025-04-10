class KeyHandler:
    """Handles keyboard input processing for the Reality Glitch game."""
    
    def __init__(self, game_instance):
        """Initialize the key handler with a reference to the game instance.
        
        Args:
            game_instance: Reference to the RealityGlitchGame instance
        """
        self.game = game_instance
        self.term = self.game.term
    
    def normalize_key(self, key):
        """Normalize function key names to consistent format.
        
        Args:
            key: The key object from blessed.Terminal.inkey()
            
        Returns:
            The same key object with normalized_name added
        """
        key_name = key.name
        if key_name and key_name.startswith('KEY_F') and not key_name.startswith('KEY_F('):
            # Convert KEY_F1 to KEY_F(1)
            num = key_name[5:]
            key_name = f'KEY_F({num})'
            
            # Show debug info about normalization if debug mode is on
            if self.game.story_engine.debug:
                print(f"Normalized key name from {key.name} to {key_name}")
        
        # Keep a reference to the original key but use normalized name
        key.normalized_name = key_name
        return key
    
    def handle_key(self, key):
        """Main entry point for handling key presses.
        
        Args:
            key: The key object from blessed.Terminal.inkey()
        """
        # Normalize the key
        key = self.normalize_key(key)
        
        # Ignore keyboard input if typewriter animation is active
        if self.game.story_engine.typewriter_active:
            return
            
        if self.game.save_menu_active:
            self.handle_save_menu_key(key)
            return
        elif self.game.load_menu_active:
            self.handle_load_menu_key(key)
            return
        
        # Get the normalized key name
        key_name = key.normalized_name
        
        if self.game.story_mode:
            # F-keys still work in story mode
            if key_name == 'KEY_F(1)':
                self.game.display_help()
            elif key_name == 'KEY_F(7)':
                self.game.display_sci_fi_animation()
            elif key_name == 'KEY_F(9)':
                self.game.save_story()
            elif key_name == 'KEY_F(10)':
                self.game.load_story()
            else:
                self.handle_story_choice(key)
        else:
            # Handle main menu keys
            if key_name == 'KEY_F(1)':
                self.game.display_help()
            elif key_name == 'KEY_F(2)':
                self.game.bitcoin()
            elif key_name == 'KEY_F(3)':
                self.game.stocks()
            elif key_name == 'KEY_F(4)':
                self.game.weather()
            elif key_name == 'KEY_F(5)':
                self.game.trigger_panic()
            elif key_name == 'KEY_F(6)':
                self.game.toggle_story_mode()
            elif key_name == 'KEY_F(7)':
                self.game.display_sci_fi_animation()
            elif key_name == 'KEY_F(9)' and self.game.story_engine.has_saved_story():
                self.game.save_story()
            elif key_name == 'KEY_F(10)' and self.game.story_engine.has_saved_story():
                self.game.load_story()
            elif key_name == 'KEY_ESCAPE':
                self.game.running = False
    
    def handle_story_choice(self, key):
        """Handle player choice in story mode.
        
        Args:
            key: The key object from blessed.Terminal.inkey()
        """
        # Skip if typewriter animation is active
        if self.game.story_engine.typewriter_active:
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
                self.game.story_mode = False
                self.game.display_welcome()
                return
            
            # Validate choice index
            if choice_index < 0 or choice_index >= len(self.game.story_engine.current_choices):
                print("\n" + self.game.error + "Invalid choice number. Please try again." + self.term.normal)
                import time
                time.sleep(1)
                self.game.display_story()
                return
                
            # Process the valid choice
            print(f"\nProcessing choice {choice_index+1}...")
            
            # Clear screen
            print(self.term.clear)
            print("\n" * 2)  # Add some padding at the top
            
            # Show the choice being made
            chosen_action = self.game.story_engine.current_choices[choice_index]
            self.game.story_engine.typewriter_effect(f"You chose: {chosen_action}", style=self.game.text_color)
            import time
            time.sleep(0.5)
            
            # Show loading status
            print("\n" + self.game.warning + "Generating response..." + self.term.normal)
            
            # Process the choice
            success, new_story, new_choices = self.game.story_engine.make_choice(choice_index)
            
            if success and new_story and new_choices and len(new_choices) >= 3:
                # Display the new story state using the enhanced UI
                self.game.display_story()
            else:
                # Show error and redisplay current state
                print("\n" + self.game.error + "The alien device buzzes angrily - even cosmic horrors appreciate valid inputs." + self.term.normal)
                print(self.game.error + "Failed to generate next story segment. Please try again." + self.term.normal)
                time.sleep(2)
                self.game.display_story()
        except Exception as e:
            print(f"\n{self.game.error}Error processing choice: {str(e)}{self.term.normal}")
            import time
            time.sleep(2)
            self.game.display_story()
    
    def handle_save_menu_key(self, key):
        """Handle key presses in the save menu.
        
        Args:
            key: The key object from blessed.Terminal.inkey()
        """
        max_selection = len(self.game.current_saves)
        redraw = False
        
        # Use normalized_name if available, otherwise use name
        key_name = getattr(key, 'normalized_name', key.name)
        
        if key_name == 'KEY_UP':
            self.game.menu_selection = (self.game.menu_selection - 1) % (max_selection + 1)
            redraw = True
        elif key_name == 'KEY_DOWN':
            self.game.menu_selection = (self.game.menu_selection + 1) % (max_selection + 1)
            redraw = True
        elif key_name == 'KEY_ESCAPE':
            # Exit the save menu
            self.game.save_menu_active = False
            
            # Redisplay the story
            self.game.display_story()
        elif key_name == 'KEY_ENTER':
            if self.game.menu_selection == 0:  # New save
                # Generate a new save ID
                save_id = self.game.story_engine.generate_save_id()
                # Generate a default title based on timestamp
                from datetime import datetime
                title = f"Reality Glitch - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                # Save the game
                if self.game.story_engine.save_story(save_id=save_id, title=title):
                    # Exit the menu
                    self.game.save_menu_active = False
                    # Show success message
                    print(self.term.clear)
                    print("\n" + self.game.text_color + "Successfully saved reality fragment." + self.term.normal)
                    import time
                    time.sleep(1)
                    # Redisplay the story
                    self.game.display_story()
                else:
                    # Show error and wait for acknowledgement
                    print("\n" + self.game.error + "Failed to save reality fragment." + self.term.normal)
                    print("Press any key to continue...")
                    self.term.inkey()
                    # Redisplay the save menu
                    self.game.display_save_menu()
            else:
                # Use an existing save
                save_id = self.game.current_saves[self.game.menu_selection - 1]['id']
                title = self.game.current_saves[self.game.menu_selection - 1]['title']
                # Save the game
                if self.game.story_engine.save_story(save_id=save_id, title=title):
                    # Exit the menu
                    self.game.save_menu_active = False
                    # Show success message
                    print(self.term.clear)
                    print("\n" + self.game.text_color + "Successfully updated reality fragment." + self.term.normal)
                    import time
                    time.sleep(1)
                    # Redisplay the story
                    self.game.display_story()
                else:
                    # Show error and wait for acknowledgement
                    print("\n" + self.game.error + "Failed to update reality fragment." + self.term.normal)
                    print("Press any key to continue...")
                    self.term.inkey()
                    # Redisplay the save menu
                    self.game.display_save_menu()
        
        # Only redraw if needed
        if redraw:
            self.game.display_save_menu()
    
    def handle_load_menu_key(self, key):
        """Handle key presses in the load menu.
        
        Args:
            key: The key object from blessed.Terminal.inkey()
        """
        if not self.game.current_saves:
            # Use normalized_name if available, otherwise use name
            key_name = getattr(key, 'normalized_name', key.name)
            
            if key_name == 'KEY_ESCAPE':
                self.game.load_menu_active = False
                # Clear the blessed terminal screen
                print(self.term.clear + self.term.home)
                # If in story mode, redisplay the story
                if self.game.story_mode:
                    self.game.display_story()
                else:
                    self.game.display_welcome()
            return
        
        redraw = False
        max_selection = len(self.game.current_saves) - 1
        
        # Use normalized_name if available, otherwise use name
        key_name = getattr(key, 'normalized_name', key.name)
        
        if key_name == 'KEY_UP':
            self.game.menu_selection = (self.game.menu_selection - 1) % (max_selection + 1)
            redraw = True
        elif key_name == 'KEY_DOWN':
            self.game.menu_selection = (self.game.menu_selection + 1) % (max_selection + 1)
            redraw = True
        elif key_name == 'KEY_ESCAPE':
            # Exit the load menu
            self.game.load_menu_active = False
            
            # Clear the blessed terminal screen
            print(self.term.clear + self.term.home)
            
            # If in story mode, redisplay the story
            if self.game.story_mode:
                self.game.display_story()
            else:
                self.game.display_welcome()
        elif key_name == 'KEY_ENTER':
            # Process the selection
            save_id = self.game.current_saves[self.game.menu_selection]['id']
            
            # Create a status message at the bottom of the screen
            message_y = self.term.height - 4
            message_x = (self.term.width - 50) // 2
            
            print(self.term.move_xy(message_x, message_y) + 
                  "A familiar cosmic shimmer appears as your saved story materializes...")
            
            # Exit the load menu before loading the story to avoid UI conflicts
            self.game.load_menu_active = False
            
            # Clear screen before loading
            print(self.term.clear)
            
            # Load the save file
            if self.game.story_engine.load_story(save_id=save_id):
                # Set flag to prevent reset when entering story mode
                self.game.loaded_from_save = True
                # Enter story mode
                if not self.game.story_mode:
                    self.game.story_mode = True
                
                # Display the story with a short delay to ensure UI is properly rendered
                import time
                time.sleep(0.5)
                # Force a redraw of the story screen
                print(self.term.clear)
                self.game.display_story()
            else:
                print(self.term.move_xy(message_x, message_y) + 
                      self.term.red + "The cosmic archives appear to be damaged. Failed to load story." + self.term.normal)
                print(self.term.move_xy(message_x, message_y + 1) + 
                      "Press any key to continue...")
                self.term.inkey()
                
                if self.game.story_mode:
                    # Redisplay the current story
                    self.game.display_story()
                else:
                    self.game.display_welcome()
        
        # Only redraw if needed
        if redraw:
            self.game.display_load_menu() 