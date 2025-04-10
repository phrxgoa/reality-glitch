import os
import json
import uuid
from datetime import datetime

class SaveManager:
    """Manages save game operations for the Reality Glitch game."""
    
    def __init__(self, save_dir=None, story_engine=None):
        """Initialize the save manager.
        
        Args:
            save_dir: Directory where save files are stored
            story_engine: Reference to StoryEngine instance
        """
        self.SAVE_DIR = save_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saved_games')
        self.story_engine = story_engine
        
        # Create save directory if it doesn't exist
        os.makedirs(self.SAVE_DIR, exist_ok=True)
    
    def get_save_files(self):
        """Get a list of save files with metadata.
        
        Returns:
            List of save file dictionaries with metadata
        """
        saves = []
        if not os.path.exists(self.SAVE_DIR):
            return saves
            
        for filename in os.listdir(self.SAVE_DIR):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.SAVE_DIR, filename), 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                        # Extract metadata for preview
                        save_meta = {
                            'id': save_data.get('id', filename[:-5]),  # Remove .json
                            'title': save_data.get('title', 'Untitled Save'),
                            'timestamp': save_data.get('timestamp', 'Unknown'),
                            'summary': save_data.get('summary', 'No summary available'),
                            'choices_preview': save_data.get('choices_preview', '')
                        }
                        saves.append(save_meta)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error loading save file {filename}: {e}")
                    continue
        
        # Sort by timestamp (newest first)
        saves.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return saves
    
    def has_saved_story(self):
        """Check if any saved stories exist.
        
        Returns:
            True if at least one save file exists
        """
        if not os.path.exists(self.SAVE_DIR):
            return False
            
        for filename in os.listdir(self.SAVE_DIR):
            if filename.endswith('.json'):
                return True
        return False
    
    def generate_save_id(self):
        """Generate a unique ID for a new save file.
        
        Returns:
            String with unique save ID
        """
        return str(uuid.uuid4())
    
    def save_story(self, save_id=None, title=None):
        """Save the current story state to a file.
        
        Args:
            save_id: ID for the save file (generates new one if None)
            title: Title for the save (uses default if None)
            
        Returns:
            True if save was successful
        """
        if not self.story_engine:
            print("Error: No story engine reference available for saving")
            return False
            
        # Generate a save ID if none provided
        if not save_id:
            save_id = self.generate_save_id()
            
        # Create a default title if none provided
        if not title:
            title = f"Reality Glitch - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
        # Create the save directory if it doesn't exist
        os.makedirs(self.SAVE_DIR, exist_ok=True)
        
        # Format the choices for preview
        choices_preview = "\n".join([f"- {choice}" for choice in self.story_engine.current_choices])
        
        # Create the save data structure
        save_data = {
            'id': save_id,
            'title': title,
            'timestamp': datetime.now().isoformat(),
            'summary': self.story_engine.current_story[-500:] if len(self.story_engine.current_story) > 500 else self.story_engine.current_story,
            'choices_preview': choices_preview,
            'full_story': self.story_engine.current_story,
            'current_choices': self.story_engine.current_choices,
            'story_state': self.story_engine.story_state,
            'game_version': '1.0'  # Add version info for compatibility checks
        }
        
        # Save to file
        save_path = os.path.join(self.SAVE_DIR, f"{save_id}.json")
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"Error saving story: {e}")
            return False
    
    def load_story(self, save_id):
        """Load a story from a save file.
        
        Args:
            save_id: ID of the save to load
            
        Returns:
            True if load was successful
        """
        if not self.story_engine:
            print("Error: No story engine reference available for loading")
            return False
            
        save_path = os.path.join(self.SAVE_DIR, f"{save_id}.json")
        
        if not os.path.exists(save_path):
            print(f"Save file not found: {save_path}")
            return False
            
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
            # Load the save data into the story engine
            self.story_engine.current_story = save_data.get('full_story', '')
            self.story_engine.current_choices = save_data.get('current_choices', [])
            self.story_engine.story_state = save_data.get('story_state', {})
            
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading save file: {e}")
            return False 