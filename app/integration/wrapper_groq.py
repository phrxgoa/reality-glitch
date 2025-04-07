import os
import json
from groq import Groq
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

class GroqClient:
    """
    A client for interacting with the Groq API, specifically using the Llama 70B model.
    Designed for the RealityGlitch project - a chaotic text adventure powered by real-time data.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Groq client.
        
        Args:
            api_key: Your Groq API key. If not provided, it will be read from the GROQ_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Provide it directly or set the GROQ_API_KEY environment variable.")
        
        self.client = Groq(api_key=self.api_key)
    
    def generate_completion(
        self,
        prompt: str,
        model: str = "llama3-70b-8192",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stream: bool = False,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion using the Groq API.
        
        Args:
            prompt: The prompt to generate a completion for.
            model: The model to use. Defaults to "llama3-70b-8192".
            max_tokens: The maximum number of tokens to generate.
            temperature: The temperature to use for sampling.
            top_p: The top-p value to use for sampling.
            stream: Whether to stream the response.
            stop: A string or list of strings to stop generation at.
            **kwargs: Additional parameters to pass to the API.
            
        Returns:
            The API response as a dictionary.
        """
        messages = [{"role": "user", "content": prompt}]
        
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=stream,
            stop=stop,
            **kwargs
        )
        
        # Convert the completion to a dictionary format
        return self._completion_to_dict(completion)
    
    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama3-70b-8192",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stream: bool = False,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using the Groq API.
        
        Args:
            messages: A list of message dictionaries with "role" and "content" keys.
            model: The model to use. Defaults to "llama3-70b-8192".
            max_tokens: The maximum number of tokens to generate.
            temperature: The temperature to use for sampling.
            top_p: The top-p value to use for sampling.
            stream: Whether to stream the response.
            stop: A string or list of strings to stop generation at.
            **kwargs: Additional parameters to pass to the API.
            
        Returns:
            The API response as a dictionary.
        """
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=stream,
            stop=stop,
            **kwargs
        )
        
        # Convert the completion to a dictionary format
        return self._completion_to_dict(completion)
    
    def generate_reality_glitch_content(
        self,
        world_state: Dict[str, Any],
        event: Dict[str, Any],
        content_type: str = "story_choices",
        model: str = "llama3-70b-8192",
        temperature: float = 0.9,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content for the RealityGlitch game based on world state and events.
        
        Args:
            world_state: Current state of the game world
            event: Current event that triggered the generation
            content_type: Type of content to generate (e.g., "story_choices", "joke", "npc_dialogue")
            model: The model to use
            temperature: Higher temperature for more chaotic/absurdist content
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            The API response as a dictionary
        """
        system_prompt = self._get_system_prompt(content_type)
        
        # Format the user prompt based on the world state and event
        user_prompt = self._format_user_prompt(world_state, event, content_type)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.generate_chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def _get_system_prompt(self, content_type: str) -> str:
        """
        Get the appropriate system prompt based on content type.
        
        Args:
            content_type: Type of content to generate
            
        Returns:
            System prompt string
        """
        prompts = {
            "story_choices": """You are a chaotic, absurdist game master for RealityGlitch, a text adventure where real-time data fuels absurdity.
Your job is to generate unpredictable, funny, and slightly unhinged story choices based on real-world events.
Keep responses short, bizarre, and entertaining. Embrace the chaos and absurdity.""",
            
            "joke": """You are a cynical crypto-bro comedian who finds humor in market crashes and technological glitches.
Your jokes should be absurd, slightly dark, and reference current events in the crypto or tech world.
Keep jokes short, punchy, and unexpected.""",
            
            "npc_dialogue": """You are an NPC in RealityGlitch, a chaotic text adventure where real-world events create absurd situations.
Your dialogue should be reactive to current events, slightly unhinged, and entertaining.
Keep responses short and character-appropriate."""
        }
        
        return prompts.get(content_type, prompts["story_choices"])
    
    def _format_user_prompt(self, world_state: Dict[str, Any], event: Dict[str, Any], content_type: str) -> str:
        """
        Format the user prompt based on world state, event, and content type.
        
        Args:
            world_state: Current state of the game world
            event: Current event that triggered the generation
            content_type: Type of content to generate
            
        Returns:
            Formatted user prompt string
        """
        if content_type == "story_choices":
            return f"""
Genre: Absurdist comedy.
World State: {json.dumps(world_state)}
Data Event: {json.dumps(event)}
Generate 2 chaotic story choices (1 sentence each).
"""
        elif content_type == "joke":
            return f"""
Current Event: {json.dumps(event)}
Generate a short, unhinged and dark joke about this event.
"""
        elif content_type == "npc_dialogue":
            return f"""
NPC Type: {world_state.get('npc_type', 'random character')}
Current Event: {json.dumps(event)}
Generate a short, reactive dialogue for this NPC.
"""
        else:
            return f"""
World State: {json.dumps(world_state)}
Event: {json.dumps(event)}
Generate content for: {content_type}
"""
    
    def _completion_to_dict(self, completion) -> Dict[str, Any]:
        """
        Convert a Groq completion object to a dictionary format.
        
        Args:
            completion: The completion object from the Groq API
            
        Returns:
            A dictionary representation of the completion
        """
        # Extract the message content
        message_content = completion.choices[0].message.content
        
        # Create a dictionary representation
        result = {
            "id": completion.id,
            "object": completion.object,
            "created": completion.created,
            "model": completion.model,
            "choices": [
                {
                    "index": choice.index,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content
                    },
                    "finish_reason": choice.finish_reason
                }
                for choice in completion.choices
            ],
            "usage": {
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens
            }
        }
        
        return result


# Function to be imported and used by other files
def generate_content(world_state: Dict[str, Any], event: Dict[str, Any], content_type: str = "story_choices", **kwargs) -> Dict[str, Any]:
    """
    Generate content for the RealityGlitch game based on world state and events.
    This function can be imported and used directly by other files.
    
    Args:
        world_state: Current state of the game world
        event: Current event that triggered the generation
        content_type: Type of content to generate (e.g., "story_choices", "joke", "npc_dialogue")
        **kwargs: Additional parameters to pass to the API (e.g., temperature, max_tokens)
        
    Returns:
        The API response as a dictionary
    """
    client = GroqClient()
    return client.generate_reality_glitch_content(
        world_state=world_state,
        event=event,
        content_type=content_type,
        **kwargs
    )
