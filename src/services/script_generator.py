from typing import Optional
from google import genai
from google.genai import types
from .config_service import ConfigService


class ScriptGeneratorService:
    """Service for generating comic scripts from event descriptions."""
    
    def __init__(self, config_service: ConfigService):
        """Initialize the script generator with configuration."""
        self.config = config_service
        self.client = genai.Client(api_key=self.config.get_google_api_key())
    
    def generate_script(self, event_description: str, style: Optional[str] = None) -> str:
        """
        Generate a structured comic script from an event description.
        
        Args:
            event_description: Description of the historical event or story
            style: Comic style (defaults to config setting)
        
        Returns:
            Generated script text in structured format
        """
        comic_style = style or self.config.get_comic_style()
        
        prompt = self._build_script_prompt(event_description, comic_style)
        
        try:
            response = self.client.models.generate_content(
                model=self.config.get_model_id(),
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Text']
                )
            )
            
            # Extract text from response
            script_text = ""
            if response.parts:
                for part in response.parts:
                    if part.text:
                        script_text += part.text
            
            return script_text.strip()
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate script: {str(e)}")
    
    def _build_script_prompt(self, event_description: str, style: str) -> str:
        """Build the prompt for script generation."""
        return f"""
You are a comic book writer specializing in {style} style comics. Create a detailed comic script for the following historical event:

EVENT: {event_description}

Please structure your script using the following format:

TITLE: [Comic title]

PANEL 1:
SCENE: [Detailed visual description of what's happening in this panel]
DIALOGUE: [Character dialogue, if any, each line on a separate line starting with character name]
NARRATION: [Narrative text, if any]

PANEL 2:
SCENE: [Detailed visual description]
DIALOGUE: [Dialogue lines]
NARRATION: [Narrative text]

[Continue for 4-6 panels]

Requirements:
- Create 4-6 panels that tell the complete story
- Include rich visual descriptions for each scene
- Add appropriate dialogue and narration
- Make it suitable for {style} artistic style
- Focus on key dramatic moments of the event
- Ensure historical accuracy where applicable

Begin the script now:
"""