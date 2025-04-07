import os
import time
import re
import json
from groq import Groq
from story_summarizer import StorySummarizer
import datetime
import blessed

# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
INITIAL_STORY = """
Late one night, you hear a faint shimmer - like reality itself developing a hiccup - from your least favorite corner of the apartment. 
From this cosmic belch emerge three creatures that make your old sleep paralysis demon look like a cuddly teddy bear. 
They're clutching a device that sparks with the enthusiasm of a dying firefly, their mismatched eyes wide with the kind of terror 
usually reserved for people who realize they've left the stove on... in another galaxy. What's your move?
"""

# Define save file paths - save in app/saved_games directory
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_games")
DEFAULT_SAVE_FILE = os.path.join(SAVE_DIR, "story_save.json")

# Ensure save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

SYSTEM_PROMPT = f"""
You are a sardonic game master with a PhD in cosmic horror and a minor in stand-up comedy.
Craft a suspenseful sci-fi narrative with dark humor elements based on this premise: "{INITIAL_STORY}".

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
- Story should be suspenseful with dark humor elements
- Choices should be meaningful and consequential
- Maintain consistent tone throughout all interactions
- Keep track of player's previous choices for narrative continuity

Example Perfect Response:
Story: The tallest alien makes a sound like a theremin being strangled. Their device sputters, casting shadows that move in ways shadows definitely shouldn't. From the kitchen, your microwave suddenly displays numbers in base-13.

Choices:
1. Offer them your questionable leftover pizza from last Tuesday
2. Throw the device into the fishtank and hope for the best
3. Try to communicate using interpretive dance inspired by your high school talent show
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
        self.debug = debug  # Debug flag to control logging
        self.summarizer = StorySummarizer(debug=self.debug)  # Add story summarizer
        self.summary_count = 0  # Track number of summaries performed
        self.save_id = None  # Current save identifier
        self.term = blessed.Terminal()  # Add terminal for visual effects
        
        # Simplified color scheme inspired by terminal aesthetics
        self.text_color = self.term.teal  # Main text color
        self.highlight = self.term.white  # For emphasis
        self.dim = self.term.dim  # For less important text
        self.warning = self.term.yellow  # For warnings/important info
        self.error = self.term.red  # For errors
    
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
    
    def typewriter_effect(self, text, delay=0.02, style=None):
        """Clean typewriter effect with monospace text"""
        if style is None:
            style = self.text_color
            
        for char in text:
            if char in ['.', '!', '?']:
                delay_time = delay * 2
            else:
                delay_time = delay
                
            print(style + char + self.term.normal, end='', flush=True)
            time.sleep(delay_time)
        print()
    
    def get_llm_context(self):
        """Get a compressed version of message history suitable for sending to the LLM.
        This keeps the full story context through summaries while limiting message count."""
        if len(self.messages) > 12:  # More than system prompt + summary + 5 pairs
            if self.debug:
                print(f"Compressing {len(self.messages)} messages for LLM context...")
            
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
            
            if self.debug:
                print(f"Compressed to {len(compressed)} messages for LLM")
            
            return compressed
        
        return self.messages

    def generate_story(self):
        """Generate next story segment using Groq with improved formatting enforcement"""
        try:
            # Get compressed context for LLM
            llm_context = self.get_llm_context()
            
            if self.debug:
                print(f"Generating story with {len(llm_context)} context messages")
            
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
            
            # If format is correct and we have at least 3 choices, return as is
            if has_story and has_choices and choice_count >= 3:
                return content
                
            # If format is not correct, try again with an enhanced prompt
            if self.debug:
                print("Response format incorrect, trying with explicit format reminder...")
            
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
            
            # If second attempt still lacks proper format, force it
            if "Story:" not in retry_content or "Choices:" not in retry_content:
                if self.debug:
                    print("Still formatting incorrectly, forcing format...")
                
                # Extract any narrative content
                story_text = retry_content
                if not story_text.strip():
                    story_text = "The aliens look at you expectantly, their device flickering with an otherworldly glow."
                
                # Create forced format
                forced_content = f"""
Story: {story_text.strip()}

Choices:
1. Try to communicate with the aliens
2. Examine the strange device more closely
3. Slowly back away while maintaining eye contact
"""
                return forced_content.strip()
            
            return retry_content
            
        except Exception as e:
            print(f"\nThe universe glitches... (Error: {e})")
            time.sleep(2)
            return self.generate_story()  # Retry
    
    def parse_response(self, response):
        """Extract story and choices from response using multiple strategies"""
        # Print the full response for debugging
        if self.debug:
            print("\n===== FULL LLM RESPONSE =====")
            print(response)
            print("=============================\n")
        
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
        
        if self.debug:
            print("\n===== EXTRACTED STORY =====")
            print(story)
            print("==========================\n")
        
        # Various strategies to extract choices
        choices = []
        
        # Strategy 1: Look for "Choices:" section
        choices_section = re.search(r'Choices:(.*?)(?:$)', response, re.DOTALL)
        if choices_section:
            choices_text = choices_section.group(1).strip()
            if self.debug:
                print("\n===== CHOICES SECTION =====")
                print(choices_text)
                print("===========================\n")
            
            # First try a clean numbered list pattern
            numbered_choices = re.findall(r'^\s*(\d+)\.\s+(.*?)$', choices_text, re.MULTILINE)
            for _, choice_text in numbered_choices:
                text = choice_text.strip()
                if text and not (text.startswith('[') and text.endswith(']')):
                    choices.append(text)
        
        # Strategy 2: Look for numbered choices in the entire response if needed
        if len(choices) < 3:
            if self.debug:
                print("Trying strategy 2: Extracting numbered choices from entire response")
            all_choices = re.findall(r'(?:^|\n)\s*(\d+)\.\s+(.*?)(?=\n\s*\d+\.|\n\n|$)', response, re.DOTALL)
            for _, choice_text in all_choices:
                text = choice_text.strip()
                # Skip if it's already in our list
                if text not in choices and text and not (text.startswith('[') and text.endswith(']')):
                    choices.append(text)
        
        # Strategy 3: Look for any lines that start with numbers
        if len(choices) < 3:
            if self.debug:
                print("Trying strategy 3: Extracting any lines starting with numbers")
            number_lines = re.findall(r'(?:^|\n)\s*(\d+)[\.:\)]\s+(.*?)(?=\n|$)', response, re.MULTILINE)
            for _, choice_text in number_lines:
                text = choice_text.strip()
                if text not in choices and text and not (text.startswith('[') and text.endswith(']')):
                    choices.append(text)
        
        # Strategy 4: Extract any lines that might look like options
        if len(choices) < 3:
            if self.debug:
                print("Trying strategy 4: Looking for option-like patterns")
            option_lines = re.findall(r'(?:^|\n)(?:Option|Choice|You can).*?:\s+(.*?)(?=\n|$)', response, re.IGNORECASE | re.MULTILINE)
            for choice_text in option_lines:
                text = choice_text.strip()
                if text not in choices and text and not (text.startswith('[') and text.endswith(']')):
                    choices.append(text)
        
        # Remove any placeholder-looking items
        choices = [c for c in choices if not (c.startswith('[') and c.endswith(']'))]
        
        # Ensure we only use the first 3 choices
        choices = choices[:3]
        
        if self.debug:
            print("\n===== EXTRACTED CHOICES =====")
            for i, choice in enumerate(choices, 1):
                print(f"{i}. {choice}")
            print("============================\n")
        
        # If we still don't have enough valid choices, create contextual fallbacks
        if len(choices) < 3:
            if self.debug:
                print("Using fallback choices")
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
        """Display the current story and choices with clean terminal aesthetics"""
        if not self.current_choices:
            # Clear screen
            print(self.term.clear)
            
            # Add some padding at the top
            print("\n")
            
            # Display story with clean formatting
            story_lines = self._wrap_text(self.current_story, self.term.width - 4)
            for line in story_lines:
                self.typewriter_effect(line.strip(), style=self.text_color)
            
            # Generate next story segment
            response = self.generate_story()
            new_story, choices = self.parse_response(response)
            
            if not choices:
                self.typewriter_effect("\nThe aliens stare at you expectantly, their device emitting a sound suspiciously like elevator music...",
                                     style=self.warning)
                return False
            
            self.current_choices = choices
            self.current_story = new_story
            
            # Update message history
            self.messages.append({"role": "assistant", "content": new_story})
            
            # Add spacing before choices
            print("\n")
            
            # Display choices with clean numbering
            for i, choice in enumerate(self.current_choices, 1):
                self.typewriter_effect(f"  {i}. {choice}", delay=0.01, style=self.highlight)
            
            # Add spacing after choices
            print("\n")
            
            # Display instructions with dimmed text
            print(self.dim + "Press 1, 2, or 3 to make your choice, or Esc to return to reality." + self.term.normal)
            print(self.dim + "Press F9 to save your adventure or F10 to load a saved one." + self.term.normal)
        return True
    
    def _wrap_text(self, text, width):
        """Wrap text to fit within specified width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if current_line and len(' '.join(current_line + [word])) > width:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        
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
        """Save the current story state to a JSON file with specified ID"""
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
            
            # Generate a detailed summary for the save file
            story_summary = "Cosmic horror adventure in progress..."
            if len(self.messages) > 3:
                try:
                    # Try to get a complete story summary
                    full_summary = self.summarizer.generate_summary(self.messages)
                    story_summary = full_summary
                    
                    # Extract the last 1-2 paragraphs for a more relevant preview
                    paragraphs = full_summary.split('\n\n')
                    if len(paragraphs) > 1:
                        story_summary = '\n\n'.join(paragraphs[-2:])
                    
                    # If still too long, take the last paragraph
                    if len(story_summary) > 500:
                        story_summary = paragraphs[-1]
                    
                    # Add "..." at the beginning to indicate it's a partial summary
                    if story_summary != full_summary:
                        story_summary = "...\n\n" + story_summary
                        
                except Exception as e:
                    if self.debug:
                        print(f"Error generating save summary: {e}")
                    
                    # Fallback: Use the current story segment
                    story_summary = self.current_story
                    if len(story_summary) > 500:
                        story_summary = "..." + story_summary[-500:]
            
            # Create save timestamp
            timestamp = datetime.datetime.now().isoformat()
            
            # Use provided title or generate a default one
            if not title:
                title = f"Reality Glitch - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Extract current player choices for context
            current_choices_text = ""
            if self.current_choices:
                current_choices_text = "\n\nCurrent choices:\n" + "\n".join([f"- {choice}" for choice in self.current_choices])
            
            # Prepare state to save
            state = {
                "messages": self.messages,
                "current_story": self.current_story,
                "current_choices": self.current_choices,
                "summary_count": self.summary_count,
                "timestamp": timestamp,
                "title": title,
                "summary": story_summary,
                "choices_preview": current_choices_text,
                "save_id": save_id
            }
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            
            # Print save location for reference
            if self.debug:
                print(f"Story saved successfully to: {os.path.abspath(filepath)}")
            
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
        """Load a story state from a JSON file"""
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
            
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Validate the state has the required fields
            required_fields = ["messages", "current_story", "current_choices"]
            if not all(key in state for key in required_fields):
                print("\033[31mSave file is missing required fields\033[0m")
                return False
            
            # Apply the loaded state (keeping full history)
            self.messages = state["messages"]
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