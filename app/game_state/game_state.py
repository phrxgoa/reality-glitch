from datetime import datetime, timedelta
from integration.reality_data import RealityData
from db.db_operations import DatabaseOperations
from integration.sync_apis import SyncApis

class GameState:
    """Manages the state of the Reality Glitch game."""
    
    def __init__(self, story_engine=None, debug=False):
        """Initialize the game state.
        
        Args:
            story_engine: Reference to the StoryEngine
            debug: Enable debug mode
        """
        self.db_ops = DatabaseOperations()
        self.running = True
        self.story_mode = False
        self.story_engine = story_engine
        self.loaded_from_save = False
        self.save_menu_active = False
        self.load_menu_active = False
        self.current_saves = []
        self.menu_selection = 0
        self.debug = debug
        
        # Reality data handler for reality glitches
        self.reality_data = RealityData(debug=self.debug)
        
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
    
    def toggle_story_mode(self):
        """Toggle between story mode and reality mode."""
        self.story_mode = not self.story_mode
        
        # Update state based on story mode toggle
        if self.story_mode:
            if not self.loaded_from_save:
                # Reset the story engine when entering story mode from scratch
                self.story_engine.reset()
                
                # Generate initial choices if starting a new story
                # This is crucial for displaying choices in a new game
                if not self.story_engine.current_choices:
                    # Parse the initial story to extract choices
                    initial_story = self.story_engine.current_story
                    initial_response = f"Story: {initial_story}\n\nChoices:\n1. Approach the aliens and attempt communication\n2. Observe quietly from inside your apartment\n3. Try to escape through the back door"
                    
                    story, choices = self.story_engine.parse_response(initial_response)
                    if choices and len(choices) >= 3:
                        self.story_engine.current_choices = choices
            else:
                # Reset the loaded flag
                self.loaded_from_save = False
        
        return self.story_mode
    
    def get_bitcoin_data(self):
        """Get the latest Bitcoin data from the database.
        
        Returns:
            Dictionary containing Bitcoin price data
        """
        return self.db_ops.get_latest_bitcoin_data()
    
    def get_stock_data(self):
        """Get the latest stock market data from the database.
        
        Returns:
            List of dictionaries containing stock data
        """
        return self.db_ops.get_latest_stock_data()
    
    def get_weather_data(self):
        """Get the latest weather data from the database.
        
        Returns:
            Dictionary containing weather data
        """
        return self.db_ops.get_latest_weather_data()
    
    def get_reality_glitches(self):
        """Get the current reality glitches based on real-world data.
        
        Returns:
            Dictionary containing reality glitch data
        """
        self.reality_data.refresh_data()
        return self.reality_data.get_reality_glitches()
    
    def update_menu_selection(self, direction):
        """Update the menu selection index.
        
        Args:
            direction: 'up' or 'down'
            
        Returns:
            The new menu selection index
        """
        max_selection = len(self.current_saves)
        
        if direction == 'up':
            self.menu_selection = (self.menu_selection - 1) % (max_selection + 1)
        elif direction == 'down':
            self.menu_selection = (self.menu_selection + 1) % (max_selection + 1)
            
        return self.menu_selection 