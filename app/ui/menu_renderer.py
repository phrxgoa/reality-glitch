from datetime import datetime
from .ui_renderer import UIRenderer

class MenuRenderer:
    """Handles rendering of game menus including save and load menus."""
    
    def __init__(self, terminal=None):
        """Initialize the menu renderer."""
        self.ui = UIRenderer(terminal)
        self.term = self.ui.term
    
    def display_save_menu(self, saves, menu_selection, story_engine):
        """Display the save game menu with a split screen layout.
        
        Args:
            saves: List of save game dictionaries
            menu_selection: Current menu selection index
            story_engine: Reference to the story engine for current story display
        """
        # Clear the screen once
        output = self.term.clear
        
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
        output += self.term.move_xy(header_pos, 1) + self.term.cyan + header + self.term.normal
        
        # Instructions at the bottom
        instructions = "Use ↑/↓ to navigate, Enter to select, Esc to cancel"
        instructions_pos = (terminal_width - len(instructions)) // 2
        output += self.term.move_xy(instructions_pos, terminal_height - 2) + \
                self.term.cyan + instructions + self.term.normal
        
        # Left panel - save list
        left_panel_y = 3
        output += self.term.move_xy(2, left_panel_y) + self.term.underline + \
                "Available Save Slots".ljust(left_width) + self.term.normal
        
        # Display option to create new save
        left_panel_y += 2
        if menu_selection == 0:
            output += self.term.move_xy(2, left_panel_y) + self.term.green + "> Create new save" + self.term.normal
        else:
            output += self.term.move_xy(2, left_panel_y) + "  Create new save"
        
        # Display existing saves that can be overwritten
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
            
            # Truncate title if too long
            if len(title) > left_width - 5:
                title = title[:left_width - 8] + "..."
            
            left_panel_y += 2
            if i == menu_selection:
                output += self.term.move_xy(2, left_panel_y) + self.term.green + \
                      f"> {i}. {title}" + self.term.normal
                output += self.term.move_xy(5, left_panel_y + 1) + self.term.green + \
                      f"({timestamp})" + self.term.normal
            else:
                output += self.term.move_xy(2, left_panel_y) + \
                      f"  {i}. {title}"
                output += self.term.move_xy(5, left_panel_y + 1) + \
                      f"({timestamp})"
        
        # Draw a vertical line to separate panels
        for y in range(3, terminal_height - 3):
            output += self.term.move_xy(left_width + 2, y) + "│"
        
        # Right panel - Preview/Summary
        right_panel_x = left_width + 4
        right_panel_y = 3
        
        output += self.term.move_xy(right_panel_x, right_panel_y) + self.term.underline + \
                "Story Preview".ljust(right_width) + self.term.normal
        
        right_panel_y += 2
        
        # Show preview of the selected save or current story
        preview_text = ""
        
        if menu_selection == 0 or not saves:
            # For new save, show the current story
            preview_text = "New Save - Current Story:"
            right_panel_y += 1
            output += self.term.move_xy(right_panel_x, right_panel_y) + self.term.bold + preview_text + self.term.normal
            
            # Get the last few lines of the current story
            story_preview = story_engine.current_story
            # Limit to last 300 chars to fit in the panel
            if len(story_preview) > 300:
                story_preview = "..." + story_preview[-300:]
            
            # Wrap text to fit the right panel and left-align
            right_panel_y += 1
            for line in self.ui.wrap_text(story_preview, right_width):
                output += self.term.move_xy(right_panel_x, right_panel_y) + line
                right_panel_y += 1
                if right_panel_y >= terminal_height - 6:  # Leave room for choices
                    break
            
            # Display current choices, left-aligned
            if story_engine.current_choices:
                right_panel_y += 1
                output += self.term.move_xy(right_panel_x, right_panel_y) + self.term.bold + "Current Choices:" + self.term.normal
                right_panel_y += 1
                
                for i, choice in enumerate(story_engine.current_choices, 1):
                    # Truncate choice if too long
                    if len(choice) > right_width - 5:
                        choice = choice[:right_width - 8] + "..."
                    
                    output += self.term.move_xy(right_panel_x, right_panel_y) + f"{i}. {choice}"
                    right_panel_y += 1
                    if right_panel_y >= terminal_height - 3:
                        break
        else:
            # Show preview of the selected save
            selected_save = saves[menu_selection - 1]
            preview_text = f"Save Preview: {selected_save.get('title', 'Untitled')}"
            right_panel_y += 1
            output += self.term.move_xy(right_panel_x, right_panel_y) + self.term.bold + preview_text + self.term.normal
            
            # Get the story summary from the save
            story_summary = selected_save.get('summary', 'No preview available')
            
            # Wrap text to fit the right panel and left-align
            right_panel_y += 2
            summary_lines = 0
            for line in self.ui.wrap_text(story_summary, right_width):
                output += self.term.move_xy(right_panel_x, right_panel_y) + line
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
                    output += self.term.move_xy(right_panel_x, right_panel_y) + self.term.bold + "Choices at Save Point:" + self.term.normal
                    right_panel_y += 1
                    
                    for i, choice in enumerate(choices, 1):
                        # Truncate choice if too long
                        if len(choice) > right_width - 5:
                            choice = choice[:right_width - 8] + "..."
                        
                        output += self.term.move_xy(right_panel_x, right_panel_y) + f"{i}. {choice}"
                        right_panel_y += 1
                        if right_panel_y >= terminal_height - 3:
                            break
        
        print(output)
        return output

    def display_load_menu(self, saves, menu_selection):
        """Display the load game menu with a split screen layout.
        
        Args:
            saves: List of save game dictionaries
            menu_selection: Current menu selection index
        """
        # Clear the screen once
        output = self.term.clear
        
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
        output += self.term.move_xy(header_pos, 1) + self.term.cyan + header + self.term.normal
        
        # Instructions at the bottom
        if saves:
            instructions = "Use ↑/↓ to navigate, Enter to select, Esc to cancel"
            instructions_pos = (terminal_width - len(instructions)) // 2
            output += self.term.move_xy(instructions_pos, terminal_height - 2) + \
                  self.term.cyan + instructions + self.term.normal
        
        # Left panel - save list
        left_panel_y = 3
        output += self.term.move_xy(2, left_panel_y) + self.term.underline + \
              "Saved Reality Fragments".ljust(left_width) + self.term.normal
        
        # Display available saves
        if not saves:
            left_panel_y += 2
            output += self.term.move_xy(2, left_panel_y) + self.term.yellow + \
                  "No saved games found." + self.term.normal
            output += self.term.move_xy(2, left_panel_y + 2) + \
                  "Press Esc to return."
        else:
            for i, save in enumerate(saves):
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
                if i == menu_selection:
                    output += self.term.move_xy(2, left_panel_y) + self.term.green + \
                          f"> {i+1}. {title}" + self.term.normal
                    output += self.term.move_xy(5, left_panel_y + 1) + self.term.green + \
                          f"({timestamp})" + self.term.normal
                else:
                    output += self.term.move_xy(2, left_panel_y) + \
                          f"  {i+1}. {title}"
                    output += self.term.move_xy(5, left_panel_y + 1) + \
                          f"({timestamp})"
        
        # Draw a vertical line to separate panels
        for y in range(3, terminal_height - 3):
            output += self.term.move_xy(left_width + 2, y) + "│"
        
        # Right panel - Preview/Summary
        if saves:
            right_panel_x = left_width + 4
            right_panel_y = 3
            
            output += self.term.move_xy(right_panel_x, right_panel_y) + self.term.underline + \
                  "Story Preview".ljust(right_width) + self.term.normal
            
            right_panel_y += 2
            
            # Show preview of the selected save
            selected_save = saves[menu_selection]
            preview_text = f"Fragment: {selected_save.get('title', 'Untitled')}"
            output += self.term.move_xy(right_panel_x, right_panel_y) + self.term.bold + preview_text + self.term.normal
            
            # Get the story summary from the save
            story_summary = selected_save.get('summary', 'No preview available')
            
            # Wrap text to fit the right panel and left-align
            right_panel_y += 2
            summary_lines = 0
            for line in self.ui.wrap_text(story_summary, right_width):
                output += self.term.move_xy(right_panel_x, right_panel_y) + line
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
                    output += self.term.move_xy(right_panel_x, right_panel_y) + self.term.bold + "Choices at Save Point:" + self.term.normal
                    right_panel_y += 1
                    
                    for i, choice in enumerate(choices, 1):
                        # Truncate choice if too long
                        if len(choice) > right_width - 5:
                            choice = choice[:right_width - 8] + "..."
                        
                        output += self.term.move_xy(right_panel_x, right_panel_y) + f"{i}. {choice}"
                        right_panel_y += 1
                        if right_panel_y >= terminal_height - 3:
                            break
        
        print(output)
        return output 