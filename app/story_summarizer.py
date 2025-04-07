import os
import json
import time
import sys
from groq import Groq

# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Define how many message pairs should trigger a summary
SUMMARY_THRESHOLD = 5  # Summarize after 5 pairs of exchanges

# Summarizer prompt
SUMMARY_PROMPT = """
You are a professional narrative summarization engine. Your task is to condense a cosmic horror story's events and keep the important details.

I will provide you with a conversation history of a story about aliens and cosmic horror with dark humor elements. 
Please create a concise summary of what has happened so far, focusing on:

1. The main events and choices made
2. Important characters and objects introduced
3. Significant developments in the plot
4. The current situation the player faces

Your summary should be written in third person and be no more than 350 words. 
DO NOT include any choices or options in your summary.
Focus ONLY on narrating what has already happened in the story, not what might happen next.

IMPORTANT: This summary will be used by the story generation system to maintain continuity,
so include key details that affect the ongoing narrative.
"""

class StorySummarizer:
    def __init__(self, debug=False):
        """Initialize the story summarizer"""
        self.groq_client = Groq(api_key=GROQ_API_KEY)
        self.debug = debug  # Debug flag to control logging
    
    def _show_progress(self, prefix="Condensing cosmic narrative", suffix="complete", duration=3):
        """Display a fancy progress indicator for summarization"""
        if self.debug:
            return  # Skip visual effects in debug mode
        
        # Cool sci-fi style condensing animation
        symbols = "▒▓█▓▒░"
        delay = duration / (80 * len(symbols))
        
        print()  # Start on new line
        for i in range(80):
            for symbol in symbols:
                sys.stdout.write(f"\r\033[36m{prefix} {symbol} {i+1}% {suffix}\033[0m")
                sys.stdout.flush()
                time.sleep(delay)
        
        print("\n")  # End with new line
    
    def should_summarize(self, messages):
        """Determine if we should summarize the story based on message count.
        
        We look for actual story exchanges (user-assistant pairs) excluding the initial
        system prompt and the initial story.
        """
        # Count the number of actual exchanges (user + assistant pairs)
        # Start from index 2 to skip system prompt and initial story
        exchange_count = 0
        
        for i in range(2, len(messages), 2):
            # Check if we have a user-assistant pair
            if i+1 < len(messages) and messages[i]["role"] == "user" and messages[i+1]["role"] == "assistant":
                exchange_count += 1
        
        # Return True if we've reached the threshold for summarization
        return exchange_count >= SUMMARY_THRESHOLD
    
    def generate_summary(self, messages):
        """Generate a summary of the story so far"""
        if self.debug:
            print("Generating story summary...")
        
        # Extract the actual story content from messages
        story_content = []
        
        # Skip the first system message but keep the initial story
        for message in messages[1:]:
            # Only include content from user and assistant messages
            if message["role"] in ["user", "assistant"]:
                story_content.append(f"{message['role'].upper()}: {message['content']}")
        
        # Join all story content
        full_story = "\n\n".join(story_content)
        
        # Create the summarization request
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",  # Using the same model for consistency
                messages=[
                    {"role": "system", "content": SUMMARY_PROMPT},
                    {"role": "user", "content": f"Here is the story so far:\n\n{full_story}\n\nPlease summarize this narrative."}
                ],
                temperature=0.3,  # Lower temperature for more consistent summaries
                max_tokens=500
            )
            
            summary = response.choices[0].message.content.strip()
            
            if self.debug:
                print("\n===== STORY SUMMARY =====")
                print(summary)
                print("=========================\n")
            
            return summary
        
        except Exception as e:
            if self.debug:
                print(f"Error generating summary: {e}")
            # Return a fallback summary if summarization fails
            return "The story has progressed with cosmic entities and strange devices. The protagonist has made several choices that have led to the current situation."
    
    def compress_history(self, messages):
        """Compress message history by replacing older exchanges with a summary"""
        if not self.should_summarize(messages):
            # Don't summarize if we haven't reached the threshold
            return messages
        
        # Show progress animation
        self._show_progress()
        
        # Generate a summary of the story so far
        summary = self.generate_summary(messages)
        
        # Keep the system prompt
        system_prompt = messages[0]
        
        # Create a new compressed history
        # Start with the system prompt
        compressed = [system_prompt]
        
        # Add a summary message
        compressed.append({
            "role": "system", 
            "content": f"STORY SUMMARY SO FAR: {summary}\n\nPlease continue the story based on this summary and the most recent exchanges."
        })
        
        # Add the most recent exchanges (keep last 2 pairs = 4 messages)
        recent_messages = messages[-4:] if len(messages) > 4 else messages[1:]
        compressed.extend(recent_messages)
        
        if self.debug:
            print(f"Compressed history from {len(messages)} to {len(compressed)} messages")
        
        return compressed


# For testing
if __name__ == "__main__":
    # Create a sample message history
    sample_messages = [
        {"role": "system", "content": "System prompt"},
        {"role": "assistant", "content": "Initial story"},
        {"role": "user", "content": "I choose option 1"},
        {"role": "assistant", "content": "Next story segment"},
        {"role": "user", "content": "I choose option 2"},
        {"role": "assistant", "content": "Another story segment"},
        {"role": "user", "content": "I choose option 3"},
        {"role": "assistant", "content": "More story content"},
        {"role": "user", "content": "I choose option 1 again"},
        {"role": "assistant", "content": "Yet more story content"},
        {"role": "user", "content": "I choose option 2 again"},
        {"role": "assistant", "content": "Final story segment"}
    ]
    
    # Test the summarizer
    summarizer = StorySummarizer(debug=True)
    
    # Check if we should summarize
    should_summarize = summarizer.should_summarize(sample_messages)
    print(f"Should summarize: {should_summarize}")
    
    # Generate a summary
    if should_summarize:
        summary = summarizer.generate_summary(sample_messages)
        print(f"Summary: {summary}")
        
        # Test compression
        compressed = summarizer.compress_history(sample_messages)
        print(f"Original message count: {len(sample_messages)}")
        print(f"Compressed message count: {len(compressed)}") 