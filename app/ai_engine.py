import os
import time
import re
import json
from groq import Groq
from story_summarizer import StorySummarizer

# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
INITIAL_STORY = """
Late one night, you hear a faint shimmer - like reality itself developing a hiccup - from your least favorite corner of the apartment. 
From this cosmic belch emerge three creatures that make your old sleep paralysis demon look like a cuddly teddy bear. 
They're clutching a device that sparks with the enthusiasm of a dying firefly, their mismatched eyes wide with the kind of terror 
usually reserved for people who realize they've left the stove on... in another galaxy. What's your move?
"""

# Define save file path - save in app directory
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SAVE_FILE = os.path.join(SAVE_DIR, "story_save.json")

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
    
    def typewriter_effect(self, text, delay=0.03):
        """Add dramatic text display"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print("\n")
    
    def generate_story(self):
        """Generate next story segment using Groq with improved formatting enforcement"""
        try:
            # Check if we need to summarize the story history
            if self.summarizer.should_summarize(self.messages):
                if self.debug:
                    print(f"Story has grown long ({len(self.messages)} messages). Summarizing...")
                
                # Compress the message history - the summarizer will show progress
                self.messages = self.summarizer.compress_history(self.messages)
                self.summary_count += 1
                
                if self.debug:
                    print(f"History compressed. Summary count: {self.summary_count}")
            
            # First attempt with regular prompt
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=self.messages,
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
            reminder_messages = self.messages.copy()
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
        """Display the current story and choices"""
        # Only clear the screen when generating a new story segment
        if not self.current_choices:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.typewriter_effect(f"\n{self.current_story}\n")
            
            # Generate next story segment
            response = self.generate_story()
            new_story, choices = self.parse_response(response)
            
            if not choices:
                self.typewriter_effect("\nThe aliens stare at you expectantly, their device emitting a sound suspiciously like elevator music...")
                return False
            
            self.current_choices = choices
            self.current_story = new_story
            
            # Update message history
            self.messages.append({"role": "assistant", "content": new_story})
            
            # Display choices
            for i, choice in enumerate(self.current_choices, 1):
                self.typewriter_effect(f"{i}. {choice}", delay=0.05)
            
            print("\nPress 1, 2, or 3 to make your choice, or Esc to return to reality.")
            print("Press F9 to save your adventure or F10 to load a saved one.")
        return True
    
    def make_choice(self, choice_index):
        """Process player's choice and update story state"""
        if 0 <= choice_index < len(self.current_choices):
            chosen_action = self.current_choices[choice_index]
            
            # Clear the screen for the next story segment
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Display the choice being made
            self.typewriter_effect(f"\nYou chose: {chosen_action}")
                        
            time.sleep(0.5)  # Brief pause
            
            # Update message history with player's choice
            self.messages.append({"role": "user", "content": f"I choose to: {chosen_action}"})
            
            # Reset choices to trigger generation of next story segment
            self.current_choices = []
            
            try:
                # Generate the next story segment with status indicator
                if not self.debug:
                    print("Generating cosmic response...", end="", flush=True)
                    
                    # Check if we're approaching summarization threshold
                    exchange_count = 0
                    for i in range(2, len(self.messages), 2):
                        if i+1 < len(self.messages) and self.messages[i]["role"] == "user" and self.messages[i+1]["role"] == "assistant":
                            exchange_count += 1
                    
                    # If we're one away from threshold, show a hint
                    if exchange_count == 4:  # One less than SUMMARY_THRESHOLD in story_summarizer.py
                        print(" \033[33m(Reality memory approaching capacity)\033[0m", end="", flush=True)
                    
                    for _ in range(5):
                        time.sleep(0.5)
                        print(".", end="", flush=True)
                    print("\n")
                else:
                    print("Generating next story segment...")
                
                # Get the story response from the LLM
                response = self.generate_story()
                new_story, choices = self.parse_response(response)
                
                if self.debug:
                    print(f"Found {len(choices)} valid choices")
                
                if choices:
                    self.current_choices = choices
                    self.current_story = new_story
                    
                    # Update message history with the new story
                    formatted_content = f"Story: {new_story}\n\nChoices:\n" + "\n".join([f"{i+1}. {c}" for i, c in enumerate(choices)])
                    self.messages.append({"role": "assistant", "content": formatted_content})
                    
                    # Clear screen again and display the new story segment
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.typewriter_effect(f"\n{self.current_story}\n")
                    
                    # Display the new choices
                    for i, choice in enumerate(self.current_choices, 1):
                        self.typewriter_effect(f"{i}. {choice}", delay=0.05)
                    
                    print("\nPress 1, 2, or 3 to make your choice, or Esc to return to reality.\n")
                    print("Press F9 to save your adventure or F10 to load a saved one.")
                    return True
                else:
                    print("Error: The cosmic narrative has encountered a glitch.")
                    print("No valid choices were generated. Please try again.")
                    time.sleep(2)
                    return False
            except Exception as e:
                print(f"\nThe universe glitches... (Error: {e})")
                time.sleep(2)
                return False
        return False
    
    def save_story(self, filepath=DEFAULT_SAVE_FILE):
        """Save the current story state to a JSON file"""
        try:
            # Ensure the directory exists
            save_dir = os.path.dirname(filepath)
            os.makedirs(save_dir, exist_ok=True)
            
            # Check if the directory is writable
            if not os.access(save_dir, os.W_OK):
                print(f"\033[31mError: Directory is not writable: {save_dir}\033[0m")
                print("Please check permissions or choose a different save location.")
                return False
            
            # Prepare state to save
            state = {
                "messages": self.messages,
                "current_story": self.current_story,
                "current_choices": self.current_choices,
                "summary_count": self.summary_count
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
            print(f"Attempted to save to: {os.path.abspath(filepath)}")
            return False
    
    def load_story(self, filepath=DEFAULT_SAVE_FILE):
        """Load a story state from a JSON file"""
        try:
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
            
            # Apply the loaded state
            self.messages = state["messages"]
            self.current_story = state["current_story"]
            self.current_choices = state["current_choices"]
            
            # Load summary count if available (for backward compatibility)
            if "summary_count" in state:
                self.summary_count = state["summary_count"]
            
            if self.debug:
                print(f"Successfully loaded story from: {os.path.abspath(filepath)}")
            
            return True
        except Exception as e:
            print(f"\033[31mError loading story: {e}\033[0m")
            print(f"Attempted to load from: {os.path.abspath(filepath)}")
            return False
            
    def has_saved_story(self, filepath=DEFAULT_SAVE_FILE):
        """Check if a saved story exists"""
        exists = os.path.exists(filepath)
        if self.debug:
            if exists:
                print(f"Found save file at: {os.path.abspath(filepath)}")
            else:
                print(f"No save file found at: {os.path.abspath(filepath)}")
        return exists
        
    def reset(self):
        """Reset the story engine to its initial state"""
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": INITIAL_STORY}
        ]
        self.current_story = INITIAL_STORY
        self.current_choices = []

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