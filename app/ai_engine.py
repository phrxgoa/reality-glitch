import os
import time
import re
import json
from groq import Groq
from story_summarizer import StorySummarizer
from integration.reality_data import RealityData
import datetime
import blessed
import random

# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
INITIAL_STORY = """
At 2:37 AM, your apartment's ambient radiation detector sounds a low-level alert. Simultaneously, your electronic devices power cycle. Through your window, an iridescent light silently descends into the parking lot. When it dissipates, three humanoid figures of varying heights stand beneath the sodium lamps. Their environmental suits suggest non-Earth origin, with breathing apparatus and protective layers against unknown contaminants. One holds a device emitting regular pulses of coherent light—possibly a scanning or communication tool. They approach your door with methodical precision, their movements suggesting purposeful intent rather than threat. What course of action will you take?
"""

# Define save file paths - save in app/saved_games directory
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_games")
DEFAULT_SAVE_FILE = os.path.join(SAVE_DIR, "story_save.json")

# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

SYSTEM_PROMPT = f"""
You are a meticulous science fiction author in the tradition of Isaac Asimov, Arthur C. Clarke, and Frank Herbert.
Craft a logical, scientifically plausible narrative based on this premise: "{INITIAL_STORY}".

CRITICAL: You MUST maintain EXACT format for EVERY response in this conversation:

Story: [Your narrative text here - do not include the brackets in your response]

Choices:
1. [Specific action choice 1 - do not include the brackets in your response]
2. [Specific action choice 2 - do not include the brackets in your response]
3. [Specific action choice 3 - do not include the brackets in your response]

Format Rules:
- ALWAYS include "Story:" followed by your narrative
- ALWAYS include "Choices:" as a separate line
- ALWAYS provide EXACTLY THREE numbered choices (1., 2., 3.)
- NEVER use placeholder text with brackets like [this] in your actual response
- ALWAYS make each choice a specific, concrete action (not a generic placeholder)
- NEVER skip the format even after several exchanges

Content Guidelines:
- Adhere to hard science fiction principles: use real scientific concepts and logical extrapolations
- Focus on technological implications, scientific accuracy, and logical consequences
- Maintain narrative consistency with previously established details
- Approach anomalous occurrences with rational explanations grounded in theoretical science
- Avoid supernatural explanations, magical elements, or fantasy tropes
- Keep track of player's previous choices for narrative continuity

Example Perfect Response:
Story: The tallest visitor makes a series of clicks and whistles that your ears interpret as language through some unknown mechanism. Their device emits controlled electromagnetic pulses, causing your microwave's display to cycle through numerical sequences—likely an attempt at establishing a mathematical basis for communication.

Choices:
1. Retrieve your tablet and open a graphing calculator app to demonstrate basic mathematical principles
2. Examine the visitors' device more closely to identify its components and operating principles
3. Draw a simple diagram of our solar system to establish common astronomical knowledge
"""

class StoryEngine:
    def __init__(self, debug=False):
        """Initialize the story engine with Groq client and initial story state"""
        self.groq_client = Groq(api_key=GROQ_API_KEY)
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": INITIAL_STORY}
        ]
        self.current_story = INITIAL_STORY
        self.current_choices = []
        self.debug = debug  # Debug flag to control logging, but we'll suppress most output anyway
        self.summarizer = StorySummarizer(debug=False)  # Force debug off for summarizer
        self.reality_data = RealityData(debug=False)  # Force debug off for reality data
        self.summary_count = 0  # Track number of summaries performed
        self.save_id = None  # Current save identifier
        self.term = blessed.Terminal()  # Add terminal for visual effects
        self.typewriter_active = False  # Flag to track if typewriter animation is currently playing
        
        # Enhanced color scheme for better sci-fi aesthetics
        self.text_color = self.term.teal  # Main text color
        self.highlight = self.term.white  # For emphasis
        self.dim = self.term.dim  # For less important text
        self.warning = self.term.yellow  # For warnings/important info
        self.error = self.term.red  # For errors
        self.anomaly = self.term.bright_magenta  # For reality glitches
    
    def draw_border(self, x, y, width, height, title=""):
        """Draw a fancy border around text"""
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
    
    def typewriter_effect(self, text, delay=0.02, style=None, glitch_chance=0.005, x=None, y=None):
        """Advanced typewriter effect with occasional glitches for sci-fi immersion"""
        self.typewriter_active = True  # Set the flag that typewriter is active
        
        if style is None:
            style = self.text_color
        
        # Characters that pause for dramatic effect    
        pause_chars = ['.', '!', '?', ':', ';']
        
        # Flush any existing input before starting
        self._flush_input()
        
        try:
            current_x = x  # Track current x position if provided
            
            for i, char in enumerate(text):
                # Move to position if coordinates provided
                if x is not None and y is not None:
                    print(self.term.move_xy(current_x, y), end='')
                    
                # Every 5 characters, flush any pending input
                if i % 5 == 0:
                    self._flush_input()
                
                # Determine the delay for this character
                if char in pause_chars:
                    delay_time = delay * 3  # Longer pause at punctuation
                else:
                    delay_time = delay
                    
                # Occasional glitch effect (random character replacement or color change)
                if random.random() < glitch_chance:
                    # Choose a glitch type
                    glitch_type = random.choice(['char', 'color', 'flicker'])
                    
                    if glitch_type == 'char':
                        # Replace with a random "glitchy" character
                        glitch_chars = "▒▓█░▄▀▐▌┌┐└┘│┤╡╢╖╕╣║╗╝╜╛┴┬┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌"
                        if x is not None and y is not None:
                            print(self.term.move_xy(current_x, y), end='')
                        print(self.anomaly + random.choice(glitch_chars) + self.term.normal, end='', flush=True)
                        time.sleep(delay_time * 0.5)  # Shorter delay for glitch
                        if x is not None and y is not None:
                            print(self.term.move_xy(current_x, y), end='')
                        
                        # Flush input that might have arrived during this effect
                        self._flush_input()
                    
                    elif glitch_type == 'color':
                        # Show the character in glitch color
                        print(self.anomaly + char + self.term.normal, end='', flush=True)
                        if x is not None:
                            current_x += 1
                    
                    elif glitch_type == 'flicker':
                        # Flicker effect - rapidly show/hide
                        if x is not None and y is not None:
                            print(self.term.move_xy(current_x, y), end='')
                        print(' ', end='', flush=True)
                        time.sleep(delay_time * 0.2)
                        if x is not None and y is not None:
                            print(self.term.move_xy(current_x, y), end='')
                        time.sleep(delay_time * 0.1)
                        
                        # Flush input that might have arrived during this effect
                        self._flush_input()
                
                # Print the actual character
                print(style + char + self.term.normal, end='', flush=True)
                if x is not None:
                    current_x += 1
                time.sleep(delay_time)
                
                # For longer pauses after punctuation, check for input more frequently
                if char in pause_chars:
                    # Flush input that might have arrived during the punctuation pause
                    self._flush_input()
            
            if x is None:  # Only print newline if not using fixed position
                print()
            
            # Final flush to clear any pending input that accumulated during the animation
            self._flush_input()
            
            # Add a small delay before accepting input again
            time.sleep(0.1)
            self._flush_input()
                
        finally:
            self.typewriter_active = False  # Reset the flag when animation is complete
            
    def _flush_input(self):
        """Helper method to flush all pending terminal input"""
        try:
            # Keep reading keys with zero timeout until none left
            while self.term.inkey(timeout=0):
                pass
        except Exception:
            # Silently ignore any errors during flushing
            pass
    
    def get_llm_context(self):
        """Get a compressed version of message history suitable for sending to the LLM.
        This keeps the full story context through summaries while limiting message count."""
        if len(self.messages) > 12:  # More than system prompt + summary + 5 pairs
            # Keep system prompt
            system_prompt = self.messages[0]
            
            # Generate summary of older messages
            summary = self.summarizer.generate_summary(self.messages[:-10])  # Summarize all but last 5 pairs
            
            # Create compressed context
            compressed = [
                system_prompt,
                {"role": "system", "content": f"STORY SUMMARY SO FAR: {summary}\n\nPlease continue the story based on this summary and the most recent exchanges."}
            ]
            
            # Add the most recent exchanges (last 5 pairs = 10 messages)
            compressed.extend(self.messages[-10:])
            
            return compressed
        
        return self.messages

    def generate_story(self):
        """Generate next story segment using Groq with improved formatting enforcement and reality glitches"""
        try:
            # Get compressed context for LLM
            llm_context = self.get_llm_context()
            
            # Enhance the system prompt with reality glitches
            if llm_context and len(llm_context) > 0 and llm_context[0]["role"] == "system":
                original_system_prompt = llm_context[0]["content"]
                enhanced_system_prompt = self.reality_data.enhance_prompt(original_system_prompt)
                llm_context[0]["content"] = enhanced_system_prompt
            
            # First attempt with regular prompt
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=llm_context,
                temperature=0.7,
                max_tokens=1000
            )

            content = response.choices[0].message.content
            
            # Check if the response has the required format
            has_story = "Story:" in content
            has_choices = "Choices:" in content
            
            # Count the number of choices using regex
            choice_count = len(re.findall(r'(?:^|\n)\s*\d+\.', content))
            
            # If format is correct and we have at least 3 choices, enhance with reality glitches
            if has_story and has_choices and choice_count >= 3:
                # Extract the story part and enhance it with reality glitches
                story_match = re.search(r'Story:(.*?)(?:Choices:|$|\n\d+\.)', content, re.DOTALL)
                if story_match:
                    story_text = story_match.group(1).strip()
                    enhanced_story_text = self.reality_data.enhance_story(story_text)
                    
                    # Replace the original story with the enhanced one
                    content = content.replace(story_match.group(0), f"Story: {enhanced_story_text}")
                
                return content
                
            # If format is not correct, try again with an enhanced prompt
            
            # Make a more explicit format reminder
            format_reminder = """
CRITICAL FORMAT REMINDER: Your response MUST follow this EXACT structure:

Story: [Continue the narrative based on the player's choice]

Choices:
1. [Specific action choice 1]
2. [Specific action choice 2]
3. [Specific action choice 3]

DO NOT use placeholder text in brackets. Replace with actual content.
"""
            # Add format reminder to messages
            reminder_messages = llm_context.copy()
            reminder_messages.append({"role": "system", "content": format_reminder})
            
            # Second attempt with explicit format reminder
            retry_response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=reminder_messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            retry_content = retry_response.choices[0].message.content
            
            # Extract and enhance the story part if available
            story_match = re.search(r'Story:(.*?)(?:Choices:|$|\n\d+\.)', retry_content, re.DOTALL)
            if story_match:
                story_text = story_match.group(1).strip()
                enhanced_story_text = self.reality_data.enhance_story(story_text)
                
                # Replace the original story with the enhanced one
                retry_content = retry_content.replace(story_match.group(0), f"Story: {enhanced_story_text}")
            
            # If second attempt still lacks proper format, force it
            if "Story:" not in retry_content or "Choices:" not in retry_content:
                # Extract any narrative content
                story_text = retry_content
                if not story_text.strip():
                    story_text = "The aliens look at you expectantly, their device flickering with an otherworldly glow."
                
                # Enhance the story with reality glitches
                enhanced_story_text = self.reality_data.enhance_story(story_text)
                
                # Create forced format
                forced_content = f"""
Story: {enhanced_story_text.strip()}

Choices:
1. Try to communicate with the aliens
2. Examine the strange device more closely
3. Slowly back away while maintaining eye contact
"""
                return forced_content.strip()
            
            return retry_content
            
        except Exception as e:
            # Instead of printing error, add subtle glitch effects
            return """
Story: The universe ripples around you, a momentary discontinuity in the fabric of reality. The figures' outlines blur and refocus as your perception stabilizes. Their devices emit an irregular pattern of light—possibly a response to the quantum fluctuation you both experienced.

Choices:
1. Wait calmly for the reality stabilization to complete
2. Focus on the device's emission pattern to identify any mathematical sequence
3. Ask the entities if they experienced the same distortion
"""
    
    def parse_response(self, response):
        """Extract story and choices from response using multiple strategies"""
        # Extract the story part using different possible formats
        story = ""
        story_match = re.search(r'Story:(.*?)(?:Choices:|$|\n\d+\.)', response, re.DOTALL)
        if story_match:
            story = story_match.group(1).strip()
        else:
            # Fallback - take everything up to the first numbered item if no Story: tag
            story_match = re.search(r'^(.*?)(?:\n\s*\d+\.|\nChoices:)', response, re.DOTALL)
            if story_match:
                story = story_match.group(1).strip()
            else:
                # Last resort - if no structure, take everything
                story = response.strip()
        
        # Various strategies to extract choices
        choices = []
        
        # Strategy 1: Look for "Choices:" section
        choices_section = re.search(r'Choices:(.*?)(?:$)', response, re.DOTALL)
        if choices_section:
            choices_text = choices_section.group(1).strip()
            
            # First try a clean numbered list pattern
            numbered_choices = re.findall(r'^\s*(\d+)\.\s+(.*?)$', choices_text, re.MULTILINE)
            for _, choice_text in numbered_choices:
                text = choice_text.strip()
                if text and not (text.startswith('[') and text.endswith(']')):
                    choices.append(text)
        
        # Strategy 2: Look for numbered choices in the entire response if needed
        if len(choices) < 3:
            all_choices = re.findall(r'(?:^|\n)\s*(\d+)\.\s+(.*?)(?=\n\s*\d+\.|\n\n|$)', response, re.DOTALL)
            for _, choice_text in all_choices:
                text = choice_text.strip()
                # Skip if it's already in our list
                if text not in choices and text and not (text.startswith('[') and text.endswith(']')):
                    choices.append(text)
        
        # Strategy 3: Look for any lines that start with numbers
        if len(choices) < 3:
            number_lines = re.findall(r'(?:^|\n)\s*(\d+)[\.:\)]\s+(.*?)(?=\n|$)', response, re.MULTILINE)
            for _, choice_text in number_lines:
                text = choice_text.strip()
                if text not in choices and text and not (text.startswith('[') and text.endswith(']')):
                    choices.append(text)
        
        # Strategy 4: Extract any lines that might look like options
        if len(choices) < 3:
            option_lines = re.findall(r'(?:^|\n)(?:Option|Choice|You can).*?:\s+(.*?)(?=\n|$)', response, re.IGNORECASE | re.MULTILINE)
            for choice_text in option_lines:
                text = choice_text.strip()
                if text not in choices and text and not (text.startswith('[') and text.endswith(']')):
                    choices.append(text)
        
        # Remove any placeholder-looking items
        choices = [c for c in choices if not (c.startswith('[') and c.endswith(']'))]
        
        # Ensure we only use the first 3 choices
        choices = choices[:3]
        
        # If we still don't have enough valid choices, create contextual fallbacks
        if len(choices) < 3:
            # Create more contextual fallbacks based on the story content
            contextual_fallbacks = []
            
            # Check if story contains certain elements to create context-aware choices
            lower_story = story.lower()
            
            if "alien" in lower_story or "creature" in lower_story:
                contextual_fallbacks.append("Try to communicate with the aliens")
                contextual_fallbacks.append("Observe the aliens from a safe distance")
            
            if "device" in lower_story or "gadget" in lower_story or "machine" in lower_story:
                contextual_fallbacks.append("Examine the strange device more closely")
                contextual_fallbacks.append("Ask the aliens about the purpose of their device")
            
            if "door" in lower_story or "exit" in lower_story or "window" in lower_story:
                contextual_fallbacks.append("Make a run for the nearest exit")
            
            # Add some generic but interesting fallbacks if we need more
            generic_fallbacks = [
                "Look around for something useful in the room",
                "Try to distract them with a random object",
                "Ask them about their home planet",
                "Pretend to be an alien yourself",
                "Offer them something to eat or drink",
                "Slowly back away while maintaining eye contact"
            ]
            
            # Combine contextual and generic fallbacks
            all_fallbacks = contextual_fallbacks + generic_fallbacks
            
            # Add fallbacks until we have 3 choices
            for fallback in all_fallbacks:
                if fallback not in choices:
                    choices.append(fallback)
                    if len(choices) >= 3:
                        break
        
        # Ensure we always return exactly 3 choices
        return story, choices[:3]
    
    def display_story(self):
        """Display the current story and choices with immersive sci-fi aesthetic"""
        # Clear screen and hide cursor during setup
        print(self.term.clear + self.term.home + self.term.hide_cursor)
        
        # Set up dimensions for our interface
        terminal_width = self.term.width
        terminal_height = self.term.height
        
        # Setup title and styling constants
        title = "REALITY GLITCH PROTOCOL"
        subtitle = "QUANTUM NARRATIVE INTERFACE"
        
        # Calculate box dimensions with some padding - make box wider and taller
        box_width = min(terminal_width - 6, 110)  # Width of the outer box
        content_width = box_width - 8             # Width available for content inside the box, including margins
        text_area_width = content_width - 16      # Reduced width for actual text to ensure padding
        
        # First determine how much space the story and choices will take
        story_lines = self._wrap_text(self.current_story, text_area_width)
        story_height = len(story_lines)
        
        # Calculate height needs for choices - estimate 2 lines per choice with wrapping
        estimated_choice_lines = 0
        if self.current_choices:
            for choice in self.current_choices:
                choice_text = f"│#│ ▷ {choice}"  # Placeholder for number
                wrapped_choice = self._wrap_text(choice_text, text_area_width - 6)  # Width for choices
                estimated_choice_lines += len(wrapped_choice)
        
        # Add extra space for decorations, headers, separators and instructions
        extra_space = 20  # For headers, footers, and other UI elements
        total_content_height = story_height + estimated_choice_lines + extra_space
        
        # Calculate box height - make it larger to accommodate content
        box_height = min(total_content_height + 4, terminal_height - 2)  # Add padding and ensure it fits in terminal
        
        # Center the box on screen
        start_x = (terminal_width - box_width) // 2
        start_y = (terminal_height - box_height) // 2
        
        # Draw the main UI box
        self._draw_sci_fi_box(start_x, start_y, box_width, box_height, title)
        
        # Add subtitle
        subtitle_x = start_x + (box_width - len(subtitle)) // 2        
        print(self.term.move_xy(subtitle_x, start_y + 2) + self.highlight + subtitle + self.term.normal)
        
        # Add decorative elements (Matrix-style characters at top and bottom of box)
        self._add_matrix_decoration(start_x + 2, start_y + 3, box_width - 4)
        
        # Display story content
        content_start_y = start_y + 5  # Start content after decorations
        
        # Display timestamp and session info
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp_str = f"TIMESTAMP: {timestamp}"
        timestamp_x = start_x + box_width - len(timestamp_str) - 4
        print(self.term.move_xy(timestamp_x, content_start_y) + self.dim + timestamp_str + self.term.normal)
        
        session_id = hex(hash(str(self.messages[0])))[2:10]
        session_str = f"SESSION: {session_id}"
        session_x = start_x + 4
        print(self.term.move_xy(session_x, content_start_y) + self.dim + session_str + self.term.normal)
        
        content_start_y += 2
        
        # Reset cursor to normal for the rest of the display
        print(self.term.normal_cursor)
        
        if not self.current_choices:
            # Check if we have a current story but no choices (might be from a corrupted save)
            if self.current_story and self.current_story != self.messages[1]["content"]:
                # Display warning message
                warning_msg = "⚠ Quantum state reconstruction in progress..."
                warning_x = start_x + (box_width - len(warning_msg)) // 2
                print(self.term.move_xy(warning_x, content_start_y) + self.warning + warning_msg + self.term.normal)
                content_start_y += 1
        
        # Display the story with proper wrapping and centering
        for line in story_lines:
            if content_start_y < start_y + box_height - 12:  # Leave space for other elements
                line_text = line.strip()
                # Calculate the starting position relative to the box's left border
                # The text should be centered within the content area (box_width - 8)                
                text_start = start_x + 4  # Start 4 characters from the left border
                remaining_space = content_width - len(line_text)
                if remaining_space > 0:
                    text_start += remaining_space // 2
                
                # Instead of moving and then calling typewriter, pass coordinates to typewriter
                self.typewriter_effect(line_text, style=self.text_color, x=text_start, y=content_start_y)
                content_start_y += 1
        
        # Calculate the position for choices
        choice_position_y = content_start_y + 1
        
        # Draw a separator before choices
        self._draw_choice_separator(start_x + 3, choice_position_y, box_width - 6)
        choice_position_y += 1
        
        # Display choices header
        choice_header = "QUANTUM DECISION PATHS:"
        choice_header_x = start_x + (box_width - len(choice_header)) // 2
        print(self.term.move_xy(choice_header_x, choice_position_y) + self.highlight + choice_header + self.term.normal)
        choice_position_y += 1
        
        # Display choices with proper centering
        if self.current_choices:
            for i, choice in enumerate(self.current_choices, 1):
                choice_text = f"│{i}│ ▷ {choice}"
                wrapped_choice = self._wrap_text(choice_text, text_area_width - 6)
                
                for j, line in enumerate(wrapped_choice):
                    if choice_position_y >= start_y + box_height - 4:
                        break
                    
                    line_text = line.strip()
                    # Calculate the starting position relative to the box's left border
                    text_start = start_x + 4  # Start 4 characters from the left border
                    remaining_space = content_width - len(line_text)
                    if remaining_space > 0:
                        text_start += remaining_space // 2
                    
                    # Instead of moving and then calling typewriter, pass coordinates to typewriter
                    self.typewriter_effect(line_text, style=self.highlight, x=text_start, y=choice_position_y)
                    choice_position_y += 1
        
        # Draw a separator after choices if there's room
        if choice_position_y < start_y + box_height - 3:
            self._draw_choice_separator(start_x + 3, choice_position_y, box_width - 6)
            choice_position_y += 1
        
        # Display instructions with proper centering
        if choice_position_y < start_y + box_height - 2:
            instruction1 = "▷ Press 1, 2, or 3 to select a path"
            instruction1_x = start_x + (box_width - len(instruction1)) // 2
            print(self.term.move_xy(instruction1_x, choice_position_y) + self.dim + instruction1 + self.term.normal)
            choice_position_y += 1
        
        if choice_position_y < start_y + box_height - 1:
            instruction2 = "▷ F9: Save fragment | F10: Load fragment | ESC: Exit"
            instruction2_x = start_x + (box_width - len(instruction2)) // 2
            print(self.term.move_xy(instruction2_x, choice_position_y) + self.dim + instruction2 + self.term.normal)
        
        # Add decorative elements at the bottom of the box
        self._add_matrix_decoration(start_x + 2, start_y + box_height - 2, box_width - 4)
        
        return True
    
    def _draw_sci_fi_box(self, x, y, width, height, title=""):
        """Draw a sci-fi themed box with decorative elements."""
        # Top border with title
        print(self.term.move_xy(x, y) + self.text_color + "╔" + "═" * (width-2) + "╗" + self.term.normal)
        
        if title:
            # Add glitch effect to title
            glitch_title = ""
            for char in title:
                if random.random() < 0.1:  # 10% chance for each character to glitch
                    glitch_title += self.anomaly + char + self.text_color
                else:
                    glitch_title += char
            
            title_pos = x + (width - len(title)) // 2
            print(self.term.move_xy(title_pos, y) + self.text_color + self.term.bold + " " + glitch_title + " " + self.term.normal)
        
        # Side borders with occasional glitch characters
        for i in range(y+1, y+height-1):
            # Left border
            if random.random() < 0.05:  # 5% chance for a glitch character
                left_char = random.choice("╠╟┣┠")
                print(self.term.move_xy(x, i) + self.anomaly + left_char + self.term.normal)
            else:
                print(self.term.move_xy(x, i) + self.text_color + "║" + self.term.normal)
            
            # Right border
            if random.random() < 0.05:  # 5% chance for a glitch character
                right_char = random.choice("╣╢┫┨")
                print(self.term.move_xy(x + width - 1, i) + self.anomaly + right_char + self.term.normal)
            else:
                print(self.term.move_xy(x + width - 1, i) + self.text_color + "║" + self.term.normal)
            
            # Empty space in between
            print(self.term.move_xy(x + 1, i) + " " * (width - 2))
        
        # Bottom border
        print(self.term.move_xy(x, y+height-1) + self.text_color + "╚" + "═" * (width-2) + "╝" + self.term.normal)
    
    def _add_matrix_decoration(self, x, y, width):
        """Add Matrix-style character decoration at the specified position."""
        matrix_chars = "デテトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモヤユヨラリルレロワヲンゴザジズゼゾタダチヂッツヅテデト"
        decoration = ""
        
        for i in range(width):
            if random.random() < 0.7:  # 70% chance for a character
                char = random.choice(matrix_chars)
                # Add color variation
                if random.random() < 0.2:
                    decoration += self.anomaly + char + self.term.normal
                else:
                    decoration += self.dim + char + self.term.normal
            else:
                decoration += " "
        
        print(self.term.move_xy(x, y) + decoration)
    
    def _draw_choice_separator(self, x, y, width):
        """Draw a decorative separator before and after choices."""
        separator = self.dim + "┌" + "─" * (width-2) + "┐" + self.term.normal
        print(self.term.move_xy(x, y) + separator)
    
    def _wrap_text(self, text, width):
        """Improved text wrapping function to ensure text stays within specified width.
        Handles long words by breaking them if necessary."""
        if not text:
            return []
            
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            # Check if adding this word would exceed the width
            word_length = len(word)
            
            # If the word itself is longer than the width, we need to break it
            if word_length > width:
                # If we have existing content on the line, add it first
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = []
                    current_length = 0
                
                # Break the long word across multiple lines
                for i in range(0, word_length, width):
                    chunk = word[i:i + width]
                    if i + width < word_length:  # Not the last chunk
                        lines.append(chunk + "-")
                    else:  # Last chunk
                        current_line = [chunk]
                        current_length = len(chunk)
            else:
                # Normal case - check if word fits on current line
                if current_line and current_length + word_length + 1 > width:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
                else:
                    current_line.append(word)
                    if current_length == 0:
                        current_length = word_length
                    else:
                        current_length += word_length + 1  # +1 for the space
        
        # Add the last line if it has content
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def make_choice(self, choice_index):
        """Process the user's choice and generate the next story segment.
        Returns a tuple of (success, new_story, new_choices) if successful,
        or (False, None, None) if failed."""
        try:
            # Validate the chosen action (using 0-based index)
            if not self.current_choices or not (0 <= choice_index < len(self.current_choices)):
                if self.debug:
                    print(f"Invalid choice index: {choice_index}")
                return (False, None, None)
            
            chosen_action = self.current_choices[choice_index]
            
            # Update message history with the user's choice
            self.messages.append({"role": "user", "content": chosen_action})
            
            # Reset current choices to trigger generation of next segment
            self.current_choices = []
            
            # Generate and process the new story segment
            response = self.generate_story()
            if not response:
                if self.debug:
                    print("Failed to generate response from LLM")
                return (False, None, None)
                
            new_story, choices = self.parse_response(response)
            
            if choices and len(choices) >= 3:
                # Update current state
                self.current_story = new_story
                self.current_choices = choices
                
                # Update message history
                formatted_content = f"Story: {new_story}\n\nChoices:\n" + "\n".join([f"{i+1}. {c}" for i, c in enumerate(choices)])
                self.messages.append({"role": "assistant", "content": formatted_content})
                
                return (True, new_story, choices)
            else:
                if self.debug:
                    print(f"Failed to generate valid choices. Got: {choices}")
                return (False, None, None)
            
        except Exception as e:
            if self.debug:
                print(f"Error processing choice: {e}")
            return (False, None, None)
    
    def get_save_files(self):
        """Get a list of all saved game files with their metadata"""
        saves = []
        
        # Ensure the directory exists
        os.makedirs(SAVE_DIR, exist_ok=True)
        
        # List all json files in the save directory
        for filename in os.listdir(SAVE_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(SAVE_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    # Extract save metadata or use defaults
                    save_id = os.path.splitext(filename)[0]
                    timestamp = save_data.get('timestamp', 'Unknown date')
                    title = save_data.get('title', 'Untitled')
                    summary = save_data.get('summary', 'No summary available')
                    
                    saves.append({
                        'id': save_id,
                        'filename': filename,
                        'timestamp': timestamp,
                        'title': title,
                        'summary': summary
                    })
                except Exception as e:
                    if self.debug:
                        print(f"Error reading save file {filename}: {e}")
        
        # Sort by timestamp (newest first)
        saves.sort(key=lambda x: x['timestamp'], reverse=True)
        return saves
    
    def generate_save_id(self):
        """Generate a unique save ID based on the current timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"save_{timestamp}"
    
    def save_story(self, save_id=None, title=None):
        """Save the current story state to a JSON file with specified ID using batch writing"""
        try:
            # Generate save ID if not provided
            if not save_id:
                if self.save_id:
                    # Use existing save_id if we're updating a save
                    save_id = self.save_id
                else:
                    # Generate new save_id
                    save_id = self.generate_save_id()
            
            # Update current save ID
            self.save_id = save_id
            
            # Determine save path
            filepath = os.path.join(SAVE_DIR, f"{save_id}.json")
            
            # Ensure the directory exists
            os.makedirs(SAVE_DIR, exist_ok=True)
            
            # Check if the directory is writable
            if not os.access(SAVE_DIR, os.W_OK):
                print(f"\033[31mError: Directory is not writable: {SAVE_DIR}\033[0m")
                print("Please check permissions or choose a different save location.")
                return False
            
            # Get current timestamp - ensure this is set for all saves
            current_timestamp = datetime.datetime.now().isoformat()
            
            # Load existing save data if it exists
            if os.path.exists(filepath):
                with open(filepath, 'r+', encoding='utf-8') as f:
                    existing_state = json.load(f)
                    last_saved_index = existing_state.get('last_saved_index', 0)
                    
                    # Prepare new messages to append
                    new_messages = self.messages[last_saved_index:]
                    
                    # Update last saved index
                    last_saved_index = len(self.messages)
                    
                    # Append new messages to the existing state
                    existing_state['messages'].extend(new_messages)
                    existing_state['last_saved_index'] = last_saved_index
                    
                    # IMPORTANT: Always update current_story and current_choices to reflect current game state
                    existing_state['current_story'] = self.current_story
                    existing_state['current_choices'] = self.current_choices
                    existing_state['choices_preview'] = "\n\nCurrent choices:\n" + "\n".join([f"- {choice}" for choice in self.current_choices])
                    
                    # Always update timestamp when saving
                    existing_state['timestamp'] = current_timestamp
                    
                    f.seek(0)
                    json.dump(existing_state, f, ensure_ascii=False, indent=2)
                    f.truncate()
            else:
                # If no existing file, create a new state
                state = {
                    "messages": self.messages,
                    "current_story": self.current_story,
                    "current_choices": self.current_choices,
                    "summary_count": self.summary_count,
                    "timestamp": current_timestamp,
                    "title": title or f"Reality Glitch - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    "summary": "Cosmic horror adventure in progress...",
                    "choices_preview": "\n\nCurrent choices:\n" + "\n".join([f"- {choice}" for choice in self.current_choices]),
                    "save_id": save_id,
                    "last_saved_index": len(self.messages)
                }
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(state, f, ensure_ascii=False, indent=2)
            
            # Print save location for reference
            if self.debug:
                print(f"Story saved successfully to: {os.path.abspath(filepath)}")
                print(f"Save timestamp: {current_timestamp}")
            
            return True
        except Exception as e:
            # Always show the error message
            print(f"\033[31mError saving story: {e}\033[0m")
            print(f"Attempted to save to: {os.path.abspath(filepath) if 'filepath' in locals() else SAVE_DIR}")
            return False
    
    def ensure_message_limit(self, messages):
        """Ensure we don't exceed message limit by compressing if needed"""
        if len(messages) > 12:  # More than system prompt + summary + 5 pairs
            if self.debug:
                print(f"Message count ({len(messages)}) exceeds limit. Compressing...")
            return self.summarizer.compress_history(messages)
        return messages

    def load_story(self, save_id=None):
        """Load a story state from a JSON file, updating legacy saves if necessary"""
        try:
            # If no ID provided, try to use the current save_id or the default
            if not save_id:
                if self.save_id:
                    save_id = self.save_id
                else:
                    # Check if default save exists
                    default_save = os.path.splitext(os.path.basename(DEFAULT_SAVE_FILE))[0]
                    if os.path.exists(os.path.join(SAVE_DIR, f"{default_save}.json")):
                        save_id = default_save
                    else:
                        # Look for the most recent save
                        saves = self.get_save_files()
                        if saves:
                            save_id = saves[0]['id']
                        else:
                            print("\033[33mNo saved games found.\033[0m")
                            return False
            
            # Determine file path from save_id
            filepath = os.path.join(SAVE_DIR, f"{save_id}.json")
            
            if not os.path.exists(filepath):
                print(f"\033[33mSave file does not exist: {os.path.abspath(filepath)}\033[0m")
                return False
            
            with open(filepath, 'r+', encoding='utf-8') as f:
                state = json.load(f)
                
                # Check for legacy save format
                if 'last_saved_index' not in state:
                    # Assume all messages are new if last_saved_index is missing
                    state['last_saved_index'] = len(state['messages'])
                    f.seek(0)
                    json.dump(state, f, ensure_ascii=False, indent=2)
                    f.truncate()
                    if self.debug:
                        print("Updated legacy save format with last_saved_index.")
                
                # Validate the state has the required fields
                required_fields = ["messages", "current_story", "current_choices"]
                if not all(key in state for key in required_fields):
                    print("\033[31mSave file is missing required fields\033[0m")
                    return False
                
                # Apply the loaded state (keeping full history)
                self.messages = state["messages"]
                
                # IMPORTANT: Verify that current_story and current_choices match the last message exchange
                # If they don't match, reconstruct them from the message history
                if len(self.messages) >= 2:
                    last_assistant_message = None
                    last_user_message = None
                    
                    # Find the last assistant message with story and choices
                    for i in range(len(self.messages) - 1, 0, -1):
                        msg = self.messages[i]
                        if msg["role"] == "assistant" and "Story:" in msg["content"] and "Choices:" in msg["content"]:
                            last_assistant_message = msg
                            break
                        elif msg["role"] == "user" and last_user_message is None:
                            last_user_message = msg
                    
                    # If we found a valid last message, extract story and choices from it
                    if last_assistant_message:
                        # Parse the story and choices from the last assistant message
                        extracted_story, extracted_choices = self.parse_response(last_assistant_message["content"])
                        
                        # Update the current state to match the last message
                        self.current_story = extracted_story
                        self.current_choices = extracted_choices
                        
                        # Also update the state in the file for consistency, but don't change timestamp
                        need_to_update = False
                        if state.get('current_story') != extracted_story:
                            state['current_story'] = extracted_story
                            need_to_update = True
                            
                        if state.get('current_choices') != extracted_choices:
                            state['current_choices'] = extracted_choices
                            state['choices_preview'] = "\n\nCurrent choices:\n" + "\n".join([f"- {choice}" for choice in extracted_choices])
                            need_to_update = True
                            
                        # Only update the file if necessary, and don't touch the timestamp
                        if need_to_update:
                            f.seek(0)
                            json.dump(state, f, ensure_ascii=False, indent=2)
                            f.truncate()
                    else:
                        # If we couldn't extract from messages, use what's in the file
                        self.current_story = state["current_story"]
                        self.current_choices = state["current_choices"]
                else:
                    # Use the values from the file if not enough messages
                    self.current_story = state["current_story"]
                    self.current_choices = state["current_choices"]
                
                # Load summary count if available (for backward compatibility)
                if "summary_count" in state:
                    self.summary_count = state["summary_count"]
                else:
                    # If no summary count, estimate based on message count
                    self.summary_count = len(state["messages"]) // 10
                
                # Store the current save_id
                self.save_id = save_id
                
                # Note: We no longer update the timestamp during load
                # This was causing timestamps to change when loading, when they should
                # only change when saving
                
                if self.debug:
                    print(f"Successfully loaded story from: {os.path.abspath(filepath)}")
                    print(f"Loaded {len(self.messages)} messages from save file")
                
                return True
        except Exception as e:
            print(f"\033[31mError loading story: {e}\033[0m")
            if 'filepath' in locals():
                print(f"Attempted to load from: {os.path.abspath(filepath)}")
            return False
            
    def has_saved_story(self):
        """Check if any saved stories exist"""
        # Ensure save directory exists
        os.makedirs(SAVE_DIR, exist_ok=True)
        
        # Check if there are any .json files in the save directory
        for filename in os.listdir(SAVE_DIR):
            if filename.endswith('.json'):
                if self.debug:
                    print(f"Found save file: {filename}")
                return True
        
        # For backward compatibility, check the old default save file
        old_default = os.path.join(os.path.dirname(os.path.abspath(__file__)), "story_save.json")
        if os.path.exists(old_default):
            if self.debug:
                print(f"Found old save file at: {os.path.abspath(old_default)}")
            # Copy old save to new location with a generated ID
            try:
                save_id = self.generate_save_id()
                new_path = os.path.join(SAVE_DIR, f"{save_id}.json")
                
                with open(old_default, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                # Add metadata if missing
                if 'timestamp' not in state:
                    state['timestamp'] = datetime.datetime.now().isoformat()
                if 'title' not in state:
                    state['title'] = "Imported Legacy Save"
                if 'summary' not in state:
                    state['summary'] = "A story imported from a previous version"
                if 'save_id' not in state:
                    state['save_id'] = save_id
                
                with open(new_path, 'w', encoding='utf-8') as f:
                    json.dump(state, f, ensure_ascii=False, indent=2)
                
                if self.debug:
                    print(f"Migrated old save to: {os.path.abspath(new_path)}")
                
                return True
            except Exception as e:
                if self.debug:
                    print(f"Error migrating old save: {e}")
        
        if self.debug:
            print("No save files found")
        return False
        
    def reset(self):
        """Reset the story engine to its initial state"""
        # Reset messages to initial state
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": INITIAL_STORY}
        ]
        
        # Reset story state
        self.current_story = INITIAL_STORY
        self.current_choices = []
        self.save_id = None  # Clear the current save ID when resetting
        self.summary_count = 0  # Reset summary count
        
        # Refresh reality data
        self.reality_data.refresh_data()
        
        if self.debug:
            print("Story engine reset to initial state")

# For standalone testing
if __name__ == "__main__":
    story_engine = StoryEngine()
    
    while True:
        # Display current story segment
        if not story_engine.display_story():
            break
            
        # Get player input
        try:
            selection = input("\n> Your move (1-3) or 'quit' to abandon reality: ")
            if selection.lower() == 'quit':
                print("\nThe aliens make a disappointed kazoo noise as you exit the simulation...")
                break
                
            choice_index = int(selection) - 1
            if not story_engine.make_choice(choice_index):
                print("\nThe alien device buzzes angrily - even cosmic horrors appreciate valid inputs.")
                
        except (ValueError, IndexError):
            print("\nThe alien device buzzes angrily - even cosmic horrors appreciate valid inputs.")