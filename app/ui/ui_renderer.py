import blessed

class UIRenderer:
    """Handles common UI rendering operations for the Reality Glitch game."""
    
    def __init__(self, terminal=None):
        """Initialize the UI renderer with terminal settings."""
        self.term = terminal or blessed.Terminal()
        
        # Simplified color scheme inspired by terminal aesthetics
        self.text_color = self.term.teal  # Main text color
        self.highlight = self.term.white  # For emphasis
        self.dim = self.term.dim  # For less important text
        self.warning = self.term.yellow  # For warnings/important info
        self.error = self.term.red  # For errors
    
    def draw_box(self, x, y, width, height, title=""):
        """Draw a box with optional title."""
        # Top border with title
        box_output = self.term.move_xy(x, y) + "╔" + "═" * (width-2) + "╗"
        if title:
            title_pos = x + (width - len(title)) // 2
            box_output += self.term.move_xy(title_pos, y) + self.term.bold + f" {title} " + self.term.normal
            
        # Side borders
        for i in range(y+1, y+height-1):
            box_output += self.term.move_xy(x, i) + "║" + " " * (width-2) + "║"
            
        # Bottom border
        box_output += self.term.move_xy(x, y+height-1) + "╚" + "═" * (width-2) + "╝"
        
        return box_output
    
    def wrap_text(self, text, width):
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
    
    def center_text(self, text, width=None):
        """Center text within the given width or terminal width."""
        if width is None:
            width = self.term.width
        return (width - len(text)) // 2
    
    def typewriter_effect(self, text, delay=0.03, style=None):
        """Display text with a typewriter effect."""
        import time
        import sys
        
        style = style or self.text_color
        
        for char in text:
            sys.stdout.write(style + char + self.term.normal)
            sys.stdout.flush()
            time.sleep(delay)
        
        # Add a newline at the end
        sys.stdout.write('\n')
        sys.stdout.flush() 