import json
from integration.wrapper_groq import GroqClient

if __name__ == "__main__":
    client = GroqClient()
    
    world_state = {
        "player_location": "California/USA",
        "inventory": ["laptop", "coffee", "lucky_satoshi_coin", "twitter_famous"],
        "active_events": ["market_volatility", "raining", "cold"]
    }
    
    # NOT_AI_TEXT: The event will be trigger by real-time data. For example, the price of Bitcoin.
    event = {
        "type": "crypto_price_change",
        "asset": "Bitcoin",
        "change_percent": -5.0,
        "timestamp": "2023-11-15T14:30:00Z"
    }
    
    reality_response = client.generate_reality_glitch_content(
        world_state=world_state,
        event=event,
        content_type="story_choices",
        temperature=0.9
    )
    
    print("\nRealityGlitch story_choices response:")
    print(json.dumps(reality_response, indent=2))