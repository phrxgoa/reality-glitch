import sys
import os
import random
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import database operations
from db.db_operations import DatabaseOperations

class RealityData:
    """
    Class to integrate real-time data into the story generation.
    This creates "reality glitches" by using real-world data to influence
    the story's tone, events, and descriptions.
    """
    
    def __init__(self, debug=False):
        """Initialize the RealityData class."""
        self.db_ops = DatabaseOperations()
        self.debug = debug
        
        # Cache for data to reduce database queries
        self.cache = {
            "bitcoin": None,
            "weather": None,
            "stocks": None,
            "last_update": None
        }
        
        # Refresh data on initialization
        self.refresh_data()
    
    def refresh_data(self) -> None:
        """Refresh all cached data from the database."""
        if self.debug:
            print("Refreshing reality data from database...")
            
        try:
            self.cache["bitcoin"] = self.db_ops.get_latest_bitcoin_data()
            self.cache["weather"] = self.db_ops.get_latest_weather_data()
            self.cache["stocks"] = self.db_ops.get_latest_stock_data()
            self.cache["last_update"] = datetime.now()
            
            if self.debug:
                print("Data refresh complete")
        except Exception as e:
            if self.debug:
                print(f"Error refreshing data: {e}")
    
    def get_reality_glitches(self) -> Dict[str, Any]:
        """
        Get reality glitches based on real-time data.
        
        Returns:
            Dict[str, Any]: A dictionary containing data-driven reality glitches
        """
        # Check if data is stale (older than 10 minutes)
        if (self.cache["last_update"] is None or 
            (datetime.now() - self.cache["last_update"]).total_seconds() > 600):
            self.refresh_data()
        
        # Build the reality glitches dictionary
        glitches = {
            "weather": self._get_weather_glitches(),
            "bitcoin": self._get_bitcoin_glitches(),
            "stocks": self._get_stock_glitches(),
            "combined": self._get_combined_glitches()
        }
        
        return glitches
    
    def _get_weather_glitches(self) -> Dict[str, Any]:
        """Extract weather-based reality glitches."""
        weather_data = self.cache["weather"]
        glitches = {
            "active": False,
            "temperature": None,
            "condition": "neutral",
            "descriptors": [],
            "events": []
        }
        
        if not weather_data:
            return glitches
        
        # Mark glitch as active
        glitches["active"] = True
        
        # Extract temperature
        glitches["temperature"] = weather_data.get("temperature_c")
        
        # Set condition based on temperature
        if glitches["temperature"] is not None:
            temp = glitches["temperature"]
            if temp < 0:
                glitches["condition"] = "freezing"
                glitches["descriptors"] = [
                    "frost-covered", "ice-cold", "frigid", "frozen", 
                    "glacial", "wintry", "crystalline"
                ]
                glitches["events"] = [
                    "ice forming on surfaces", "breath visible in the air",
                    "objects becoming brittle from cold", "sounds becoming muffled"
                ]
            elif temp < 10:
                glitches["condition"] = "cold"
                glitches["descriptors"] = [
                    "chilly", "brisk", "cold", "cool", "nippy"
                ]
                glitches["events"] = [
                    "shivering slightly", "seeking warmth", 
                    "cold metal surfaces", "goosebumps forming"
                ]
            elif temp < 20:
                glitches["condition"] = "mild"
                glitches["descriptors"] = [
                    "pleasant", "mild", "comfortable", "temperate"
                ]
                glitches["events"] = [
                    "comfortable atmospheric conditions", "unremarkable temperature"
                ]
            elif temp < 30:
                glitches["condition"] = "warm"
                glitches["descriptors"] = [
                    "warm", "balmy", "summery", "pleasant"
                ]
                glitches["events"] = [
                    "slight perspiration", "seeking shade", 
                    "surfaces warm to the touch"
                ]
            else:
                glitches["condition"] = "hot"
                glitches["descriptors"] = [
                    "scorching", "searing", "sweltering", "blistering", 
                    "blazing", "sultry", "torrid"
                ]
                glitches["events"] = [
                    "heat mirages", "oppressive heat", "air distortion from heat",
                    "surfaces too hot to touch", "seeking any available cooling"
                ]
        
        # Add humidity effects if available
        humidity = weather_data.get("humidity")
        if humidity is not None:
            if humidity > 80:
                glitches["descriptors"].extend(["humid", "muggy", "sticky", "damp"])
                glitches["events"].append("air feels thick and heavy")
            elif humidity < 30:
                glitches["descriptors"].extend(["dry", "arid", "parched"])
                glitches["events"].append("static electricity crackling")
        
        # Add wind effects if available
        wind_kph = weather_data.get("wind_kph")
        if wind_kph is not None:
            if wind_kph > 30:
                glitches["descriptors"].extend(["windy", "gusty", "blustery"])
                glitches["events"].extend([
                    "objects swaying in the wind",
                    "papers flying around",
                    "hair being tussled by wind"
                ])
            elif wind_kph > 10:
                glitches["descriptors"].append("breezy")
                glitches["events"].append("gentle breeze moving light objects")
        
        return glitches
    
    def _get_bitcoin_glitches(self) -> Dict[str, Any]:
        """Extract bitcoin-based reality glitches."""
        bitcoin_data = self.cache["bitcoin"]
        glitches = {
            "active": False,
            "price": None,
            "change_1h": None,
            "change_24h": None,
            "condition": "neutral",
            "descriptors": [],
            "events": []
        }
        
        if not bitcoin_data:
            return glitches
        
        # Mark glitch as active
        glitches["active"] = True
        
        # Extract price and changes
        glitches["price"] = bitcoin_data.get("price_usd")
        glitches["change_1h"] = bitcoin_data.get("percent_change_1h")
        glitches["change_24h"] = bitcoin_data.get("percent_change_24h")
        
        # Base condition on recent price changes
        if glitches["change_1h"] is not None:
            change = glitches["change_1h"]
            
            if change < -5:  # Significant crash
                glitches["condition"] = "crashing"
                glitches["descriptors"] = [
                    "unstable", "chaotic", "deteriorating", "collapsing", 
                    "shattering", "fragmenting"
                ]
                glitches["events"] = [
                    "digital displays flickering with red numbers", 
                    "sounds of distant alarms", 
                    "technology glitching more severely",
                    "object surfaces appearing to fracture momentarily"
                ]
            elif change < -2:  # Moderate decline
                glitches["condition"] = "declining"
                glitches["descriptors"] = [
                    "uncertain", "wavering", "faltering", "fading"
                ]
                glitches["events"] = [
                    "subtle downward movements in the corner of vision",
                    "digital displays showing decreasing values",
                    "sounds occasionally distorting to lower pitches"
                ]
            elif change < 2:  # Stable
                glitches["condition"] = "stable"
                glitches["descriptors"] = [
                    "steady", "consistent", "regular", "balanced"
                ]
                glitches["events"] = [
                    "digital systems functioning normally",
                    "predictable patterns in background noise"
                ]
            elif change < 5:  # Moderate growth
                glitches["condition"] = "growing"
                glitches["descriptors"] = [
                    "energetic", "vibrant", "expanding", "brightening"
                ]
                glitches["events"] = [
                    "subtle upward movements in peripheral vision",
                    "lights seeming slightly brighter",
                    "technology functioning with extra efficiency"
                ]
            else:  # Significant growth
                glitches["condition"] = "surging"
                glitches["descriptors"] = [
                    "electric", "charged", "intense", "luminous", 
                    "brilliant", "pulsating"
                ]
                glitches["events"] = [
                    "digital displays showing rapidly increasing numbers",
                    "faint green glow around electronic objects",
                    "air seeming to vibrate with energy",
                    "sounds occasionally distorting to higher pitches"
                ]
        
        return glitches
    
    def _get_stock_glitches(self) -> Dict[str, Any]:
        """Extract stock market-based reality glitches."""
        stock_data = self.cache["stocks"]
        glitches = {
            "active": False,
            "market_direction": "neutral",
            "volatility": "low",
            "descriptors": [],
            "events": []
        }
        
        if not stock_data or len(stock_data) == 0:
            return glitches
        
        # Mark glitch as active
        glitches["active"] = True
        
        # Calculate average change across indices
        total_change_percent = 0
        count = 0
        changes = []
        
        for stock in stock_data:
            if stock.get("price") and stock.get("change"):
                change_percent = (stock["change"] / stock["price"]) * 100
                total_change_percent += change_percent
                count += 1
                changes.append(change_percent)
        
        if count > 0:
            avg_change = total_change_percent / count
            
            # Determine market direction
            if avg_change < -1.5:
                glitches["market_direction"] = "bearish"
                glitches["descriptors"] = [
                    "descending", "sinking", "diminishing", "contracting"
                ]
                glitches["events"] = [
                    "shadows appearing longer than they should be",
                    "room temperature feeling slightly colder",
                    "colors seeming less vibrant"
                ]
            elif avg_change < -0.5:
                glitches["market_direction"] = "slightly_bearish"
                glitches["descriptors"] = [
                    "cautious", "restrained", "subdued", "muted"
                ]
                glitches["events"] = [
                    "subtle feeling of heaviness in the air",
                    "colors slightly desaturated",
                    "sounds slightly dampened"
                ]
            elif avg_change <= 0.5:
                glitches["market_direction"] = "neutral"
                glitches["descriptors"] = [
                    "balanced", "steady", "unchanging", "consistent" 
                ]
                glitches["events"] = [
                    "environment maintaining consistent properties",
                    "regular, predictable physical laws"
                ]
            elif avg_change < 1.5:
                glitches["market_direction"] = "slightly_bullish"
                glitches["descriptors"] = [
                    "improving", "rising", "ascending", "elevating"
                ]
                glitches["events"] = [
                    "objects seeming slightly lighter than expected",
                    "colors appearing somewhat brighter",
                    "subtle feeling of buoyancy"
                ]
            else:
                glitches["market_direction"] = "bullish"
                glitches["descriptors"] = [
                    "soaring", "climbing", "accelerating", "amplifying"
                ]
                glitches["events"] = [
                    "gravity feeling subtly reduced",
                    "colors appearing more vibrant than normal",
                    "sounds resonating with extra clarity"
                ]
        
            # Calculate volatility (standard deviation of changes)
            if len(changes) > 1:
                mean = sum(changes) / len(changes)
                variance = sum((x - mean) ** 2 for x in changes) / len(changes)
                std_dev = float(variance) ** 0.5
                
                # Set volatility descriptor
                if std_dev < 0.5:
                    glitches["volatility"] = "low"
                    glitches["descriptors"].extend([
                        "stable", "predictable", "reliable", "constant"
                    ])
                elif std_dev < 1.5:
                    glitches["volatility"] = "moderate"
                    glitches["descriptors"].extend([
                        "fluctuating", "shifting", "variable", "uneven"
                    ])
                    glitches["events"].extend([
                        "subtle fluctuations in lighting",
                        "occasional slight disorientation"
                    ])
                else:
                    glitches["volatility"] = "high"
                    glitches["descriptors"].extend([
                        "erratic", "turbulent", "unstable", "unpredictable", 
                        "chaotic", "fractured"
                    ])
                    glitches["events"].extend([
                        "reality shimmering at the edges",
                        "sounds occasionally distorting",
                        "momentary visual glitches",
                        "brief sensations of vertigo"
                    ])
        
        return glitches
    
    def _get_combined_glitches(self) -> Dict[str, Any]:
        """Generate combined effects from all data sources."""
        # Check if we have valid data for at least one source
        if (not self.cache["bitcoin"] and 
            not self.cache["weather"] and 
            not self.cache["stocks"]):
            return {
                "intensity": "none",
                "descriptors": ["normal", "ordinary", "standard", "usual"],
                "mood": "neutral",
                "anomalies": []
            }
        
        # Count active data sources for intensity calculation
        active_sources = 0
        if self.cache["bitcoin"]:
            active_sources += 1
        if self.cache["weather"]:
            active_sources += 1
        if self.cache["stocks"] and len(self.cache["stocks"]) > 0:
            active_sources += 1
        
        # Calculate overall reality glitch intensity
        intensity = "none"
        if active_sources == 1:
            intensity = "slight"
        elif active_sources == 2:
            intensity = "moderate"
        elif active_sources == 3:
            intensity = "strong"
        
        # Generate combined glitch effects
        combined = {
            "intensity": intensity,
            "descriptors": [],
            "mood": "neutral",
            "anomalies": []
        }
        
        # Define severe anomaly triggers
        anomaly_triggers = {
            "bitcoin_crash": self.cache["bitcoin"] and self.cache["bitcoin"].get("percent_change_1h", 0) < -7,
            "bitcoin_surge": self.cache["bitcoin"] and self.cache["bitcoin"].get("percent_change_1h", 0) > 7,
            "extreme_temp": self.cache["weather"] and (
                self.cache["weather"].get("temperature_c", 20) > 35 or 
                self.cache["weather"].get("temperature_c", 20) < -10
            ),
            "market_crash": False,
            "market_boom": False
        }
        
        # Check for market extremes
        if self.cache["stocks"] and len(self.cache["stocks"]) > 0:
            total_change_percent = 0
            count = 0
            
            for stock in self.cache["stocks"]:
                if stock.get("price") and stock.get("change"):
                    change_percent = (stock["change"] / stock["price"]) * 100
                    total_change_percent += change_percent
                    count += 1
            
            if count > 0:
                avg_change = total_change_percent / count
                anomaly_triggers["market_crash"] = avg_change < -3
                anomaly_triggers["market_boom"] = avg_change > 3
        
        # Combine descriptors and generate overall mood
        moods = []
        
        # Bitcoin influence
        if self.cache["bitcoin"]:
            bitcoin_glitches = self._get_bitcoin_glitches()
            combined["descriptors"].extend(bitcoin_glitches["descriptors"])
            
            # Set mood based on bitcoin condition
            if bitcoin_glitches["condition"] == "crashing":
                moods.append("anxious")
            elif bitcoin_glitches["condition"] == "declining":
                moods.append("uneasy")
            elif bitcoin_glitches["condition"] == "stable":
                moods.append("balanced")
            elif bitcoin_glitches["condition"] == "growing":
                moods.append("optimistic")
            elif bitcoin_glitches["condition"] == "surging":
                moods.append("euphoric")
        
        # Weather influence
        if self.cache["weather"]:
            weather_glitches = self._get_weather_glitches()
            combined["descriptors"].extend(weather_glitches["descriptors"])
            
            # Set mood based on weather condition
            if weather_glitches["condition"] == "freezing":
                moods.append("stark")
            elif weather_glitches["condition"] == "cold":
                moods.append("somber")
            elif weather_glitches["condition"] == "mild":
                moods.append("neutral")
            elif weather_glitches["condition"] == "warm":
                moods.append("pleasant")
            elif weather_glitches["condition"] == "hot":
                moods.append("intense")
        
        # Stock market influence
        if self.cache["stocks"] and len(self.cache["stocks"]) > 0:
            stock_glitches = self._get_stock_glitches()
            combined["descriptors"].extend(stock_glitches["descriptors"])
            
            # Set mood based on market direction and volatility
            if stock_glitches["market_direction"] == "bearish":
                moods.append("pessimistic")
            elif stock_glitches["market_direction"] == "slightly_bearish":
                moods.append("concerned")
            elif stock_glitches["market_direction"] == "neutral":
                moods.append("steady")
            elif stock_glitches["market_direction"] == "slightly_bullish":
                moods.append("hopeful")
            elif stock_glitches["market_direction"] == "bullish":
                moods.append("enthusiastic")
            
            # Add volatility influence
            if stock_glitches["volatility"] == "high":
                moods.append("unstable")
            elif stock_glitches["volatility"] == "moderate":
                moods.append("dynamic")
        
        # Get the most frequent mood, or random selection if tied
        if moods:
            mood_counts = {}
            for mood in moods:
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            max_count = max(mood_counts.values())
            most_common_moods = [mood for mood, count in mood_counts.items() if count == max_count]
            combined["mood"] = random.choice(most_common_moods)
        
        # Generate anomalies based on triggers
        anomalies = []
        
        if anomaly_triggers["bitcoin_crash"]:
            anomalies.extend([
                "Digital displays momentarily show cascading numbers",
                "Electronics briefly malfunction, showing error codes",
                "The air feels charged with a sense of digital panic",
                "Shadows seem to darken and stretch in impossible ways",
                "Lights flicker in patterns that somehow feel mathematical"
            ])
        
        if anomaly_triggers["bitcoin_surge"]:
            anomalies.extend([
                "Electronic devices emit a subtle green glow",
                "The air crackles with unexpected static electricity",
                "Digital displays briefly show rapidly increasing numbers",
                "Light sources seem unusually bright and oversaturated",
                "Objects appear to vibrate with a strange energy"
            ])
        
        if anomaly_triggers["extreme_temp"]:
            if self.cache["weather"].get("temperature_c", 20) > 35:
                anomalies.extend([
                    "The air wavers with visible heat distortion",
                    "Surfaces appear to shimmer at the edges",
                    "Colors become unnaturally vivid and intense",
                    "A sense of time dilation makes movements seem slower",
                    "Objects cast multiple overlapping shadows"
                ])
            else:  # Cold extreme
                anomalies.extend([
                    "Breath freezes in mid-air, hanging like crystalline sculptures",
                    "Sounds become muffled and distant",
                    "Colors desaturate to near monochrome",
                    "Surfaces develop intricate frost patterns that form and reform",
                    "Time seems to slow as the cold intensifies"
                ])
        
        if anomaly_triggers["market_crash"]:
            anomalies.extend([
                "Objects appear slightly heavier, as if gravity increased",
                "Colors drain from the environment in pulses",
                "A distant sound of breaking glass occasionally echoes",
                "Vertical lines in the environment appear to bend downward",
                "Reflective surfaces momentarily show distorted versions of reality"
            ])
        
        if anomaly_triggers["market_boom"]:
            anomalies.extend([
                "Objects seem lighter, almost buoyant",
                "Colors appear unnaturally vibrant in waves",
                "A subtle upward motion appears in peripheral vision",
                "Light sources create halos that weren't there before",
                "Reflective surfaces briefly show idealized versions of reality"
            ])
        
        # Add random anomalies based on intensity
        if intensity == "moderate" or intensity == "strong":
            potential_anomalies = [
                "Objects briefly cast shadows in impossible directions",
                "Sounds occasionally play in reverse",
                "Peripheral vision reveals movement that disappears when looked at directly",
                "Reflective surfaces show a slight delay in movements",
                "Time briefly dilates, making moments stretch or compress",
                "Colors shift subtly toward unusual spectrums",
                "The taste of metal briefly appears in the mouth",
                "Static electricity affects objects in unusual ways",
                "Words spoken seem to have a subtle echo that wasn't there before",
                "Familiar objects momentarily appear foreign or wrong"
            ]
            
            # Add 1-2 for moderate, 2-4 for strong
            num_to_add = random.randint(1, 2) if intensity == "moderate" else random.randint(2, 4)
            random_anomalies = random.sample(potential_anomalies, min(num_to_add, len(potential_anomalies)))
            anomalies.extend(random_anomalies)
        
        # Add final anomalies to the combined glitches
        combined["anomalies"] = anomalies
        
        # Ensure descriptors are unique
        combined["descriptors"] = list(set(combined["descriptors"]))
        
        return combined
    
    def get_story_modifiers(self) -> Dict[str, Any]:
        """
        Generate story modifiers based on reality data.
        
        Returns:
            Dict[str, Any]: A dictionary of modifiers for story generation
        """
        glitches = self.get_reality_glitches()
        combined = glitches["combined"]
        
        # Generate system message additions based on glitches
        modifiers = {
            "intensity": combined["intensity"],
            "mood": combined["mood"],
            "descriptors": random.sample(combined["descriptors"], min(5, len(combined["descriptors"]))),
            "anomalies": random.sample(combined["anomalies"], min(3, len(combined["anomalies"]))),
            "system_message": "",
            "story_prefix": "",
        }
        
        # Specific reality data that might be relevant to the story
        specific_data = {}
        
        if glitches["bitcoin"]["active"]:
            specific_data["bitcoin_price"] = glitches["bitcoin"]["price"]
            specific_data["bitcoin_trend"] = glitches["bitcoin"]["condition"]
        
        if glitches["weather"]["active"]:
            specific_data["temperature"] = glitches["weather"]["temperature"]
            specific_data["weather_condition"] = glitches["weather"]["condition"]
        
        if glitches["stocks"]["active"]:
            specific_data["market_direction"] = glitches["stocks"]["market_direction"]
            specific_data["market_volatility"] = glitches["stocks"]["volatility"]
        
        # Create system message addition based on intensity
        if combined["intensity"] == "none":
            modifiers["system_message"] = "Keep the story realistic and grounded."
        elif combined["intensity"] == "slight":
            modifiers["system_message"] = f"""
Subtly incorporate the following reality glitch elements into your storytelling:
- Overall mood: {combined["mood"]}
- Use these descriptive elements occasionally: {', '.join(modifiers["descriptors"])}
- Minor anomalies that could happen: {random.choice(combined["anomalies"]) if combined["anomalies"] else "slight déjà vu"}
"""
        elif combined["intensity"] == "moderate":
            modifiers["system_message"] = f"""
Distinctly incorporate these reality glitch elements into your narrative:
- Overall atmosphere: {combined["mood"]}
- Frequently use these descriptive elements: {', '.join(modifiers["descriptors"])}
- Anomalies to include: {'. '.join(modifiers["anomalies"][:2])}
"""
        elif combined["intensity"] == "strong":
            modifiers["system_message"] = f"""
Prominently feature these major reality glitch elements throughout your narrative:
- Dominant atmosphere: {combined["mood"]}
- Heavily emphasize these descriptive elements: {', '.join(modifiers["descriptors"])}
- Major anomalies to weave into the story: {'. '.join(modifiers["anomalies"])}
"""
        
        # Simply set story_prefix to empty string to avoid transition phrases
        modifiers["story_prefix"] = ""
        
        return modifiers
    
    def enhance_prompt(self, system_prompt: str) -> str:
        """
        Enhance the LLM system prompt with reality glitch elements.
        
        Args:
            system_prompt: The original system prompt
            
        Returns:
            str: Enhanced system prompt with reality glitch elements
        """
        modifiers = self.get_story_modifiers()
        
        if modifiers["intensity"] == "none":
            return system_prompt
        
        # Add the reality glitch modifiers to the system prompt
        enhanced_prompt = system_prompt + "\n\n" + modifiers["system_message"]
        
        if self.debug:
            print("\nEnhanced prompt with reality glitches:")
            print(modifiers["system_message"])
        
        return enhanced_prompt
    
    def enhance_story(self, story: str) -> str:
        """
        Enhance a story by adding reality glitch elements.
        
        Args:
            story: The original story text
            
        Returns:
            str: Enhanced story with reality glitch elements
        """
        # Simply return the original story without adding transition phrases
        return story 