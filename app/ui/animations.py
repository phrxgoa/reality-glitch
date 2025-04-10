import time
import random
from .ui_renderer import UIRenderer

class AnimationManager:
    """Manages animations and special effects for the Reality Glitch game."""
    
    def __init__(self, terminal=None):
        """Initialize the animation manager."""
        self.ui = UIRenderer(terminal)
        self.term = self.ui.term
    
    def display_sci_fi_animation(self, duration=5):
        """Display an immersive sci-fi loading animation.
        
        Args:
            duration: Duration of the animation in seconds
        """
        # Clear screen and hide cursor
        print(self.term.clear)
        print(self.term.hide_cursor)
        
        # Define animation variables
        frames = ["◢◣", "◣◥", "◥◤", "◤◢"]
        colors = [self.ui.text_color, self.ui.highlight, self.ui.warning, self.term.blue, self.term.magenta]
        
        # Set the only message to match the image
        message = "Calibrating quantum entanglement matrix..."
        
        # Matrix effect elements - specifically the Japanese characters shown in the image
        matrix_chars = "デテトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモヤユヨラリルレロワヲンゴザジズゼゾタダチヂッツヅテデト"
        glitch_chars = "█▓▒░█▓▒░"
        
        # Display header
        print("\n\n")
        title = "REALITY SYNCHRONIZATION PROTOCOL"
        title_x = (self.term.width - len(title)) // 2
        print(self.term.move_xy(title_x, 2) + self.ui.highlight + self.term.bold + title + self.term.normal)
        
        # Box dimensions
        width = 70
        height = 15
        start_x = (self.term.width - width) // 2
        start_y = 4
        
        # Draw box
        print(self.ui.draw_box(start_x, start_y, width, height))
        
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
                            style = self.ui.dim
                        
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
                  self.ui.text_color + "[" + 
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
    
    def display_welcome_screen(self):
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
                print(self.term.move_xy(x + padding, y) + self.ui.text_color + line + self.term.normal)
            y += 1
        
        # Subtitle
        subtitle = "A Cosmic Horror Adventure"
        subtitle_x = (self.term.width - len(subtitle)) // 2
        print(self.term.move_xy(subtitle_x, y+1) + self.ui.highlight + subtitle + self.term.normal)
        
        # Instructions
        instructions = ["Press F1 for help. Press Esc to exit.", "Press F10 to load a saved story."]
        for i, line in enumerate(instructions):
            instr_x = (self.term.width - len(line)) // 2
            print(self.term.move_xy(instr_x, y+3+i) + self.ui.dim + line + self.term.normal)
    
    def display_help_screen(self):
        """Display help information."""
        # Clear screen
        print(self.term.clear)
        
        # Print help header
        print(self.term.bold + self.term.yellow + "\n REALITY GLITCH - HELP INFORMATION" + self.term.normal)
        print("\n" + self.ui.dim + " A cosmic horror adventure with tendrils in the real world" + self.term.normal)
        
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
        print(" " + self.term.bold + "ESC: " + self.term.normal + "Return to main menu")
        
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
        print(" " + self.ui.dim + "This is a work of fiction. Any correlation with actual ")
        print(" existential threats is purely coincidental." + self.term.normal)
        
        # Wait for key press
        print("\nPress ESC to return to main menu.")
    
    def trigger_panic_animation(self):
        """Trigger a panic event that causes multiple reality glitches."""
        # Clear screen
        print(self.term.clear)
        
        # Title
        title = "REALITY PANIC EVENT"
        title_x = (self.term.width - len(title)) // 2
        print(self.term.move_xy(title_x, 2) + self.ui.error + title + self.term.normal)
        
        # Generate some example anomalies
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
              self.ui.warning + "MULTIPLE REALITY GLITCHES DETECTED" + self.term.normal)
        
        y = 6
        for anomaly in display_anomalies:
            # Random position with jitter effect
            x = random.randint(10, self.term.width - len(anomaly) - 10)
            
            # Random style for each anomaly
            styles = [self.ui.text_color, self.ui.highlight, self.ui.warning, self.ui.error]
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
                print(self.term.move_xy(x, y) + self.ui.error + glitch_chars + self.term.normal)
            
            time.sleep(0.2)
        
        # Return to normal display
        print(self.term.clear)
        
        # Show aftermath message
        aftermsg = "Reality stabilizing... glitches contained... for now..."
        msg_x = (self.term.width - len(aftermsg)) // 2
        print(self.term.move_xy(msg_x, (self.term.height - 4) // 2) + 
              self.ui.warning + aftermsg + self.term.normal)
        
        # Footer
        footer = "Press any key to continue..."
        footer_x = (self.term.width - len(footer)) // 2
        print(self.term.move_xy(footer_x, self.term.height - 2) + 
              self.ui.dim + footer + self.term.normal) 