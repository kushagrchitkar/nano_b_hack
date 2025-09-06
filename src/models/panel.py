from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Panel:
    """Represents a single comic panel with description, dialogue, and scene details."""
    
    panel_number: int
    scene_description: str
    dialogue: List[str]
    narration: Optional[str] = None
    image_path: Optional[str] = None
    image_prompt: Optional[str] = None
    style: str = "amar_chitra_katha"
    characters_in_panel: List[str] = field(default_factory=list)
    reference_panels: List[int] = field(default_factory=list)
    
    def __post_init__(self):
        """Generate image prompt from panel details if not provided."""
        if not self.image_prompt:
            self.image_prompt = self._generate_image_prompt()
    
    def _generate_image_prompt(self, character_descriptions: Optional[dict] = None) -> str:
        """Generate a detailed image prompt for this panel without text elements."""
        prompt_parts = [
            f"This is the design philosophy of my comics. Using this style as a metric, make me the following panel:",
            f"Panel {self.panel_number} - {self.scene_description}",
            "CRITICAL REQUIREMENT: Generate ABSOLUTELY NO TEXT of any kind. No speech bubbles, no dialogue balloons, no captions, no character labels, no role indicators, no words, no letters, no signs, no banners, no titles, no names floating above characters. This must be a completely text-free visual scene showing only characters, objects, and environments through pure visual storytelling."
        ]
        
        # Add character descriptions for consistency
        if character_descriptions and self.characters_in_panel:
            prompt_parts.append("CHARACTERS IN THIS PANEL:")
            for character_name in self.characters_in_panel:
                if character_name in character_descriptions:
                    prompt_parts.append(f"- {character_name}: {character_descriptions[character_name]}")
        
        # Note: Removed dialogue and narration from the image generation prompt
        # The dialogue will be handled separately by the frontend display
        
        return " ".join(prompt_parts)
    
    def add_character(self, character_name: str) -> None:
        """Add a character to this panel if not already present."""
        if character_name not in self.characters_in_panel:
            self.characters_in_panel.append(character_name)
    
    def set_reference_panels(self, panel_numbers: List[int]) -> None:
        """Set the reference panels for visual consistency."""
        self.reference_panels = panel_numbers.copy()