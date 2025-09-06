from dataclasses import dataclass
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
    
    def __post_init__(self):
        """Generate image prompt from panel details if not provided."""
        if not self.image_prompt:
            self.image_prompt = self._generate_image_prompt()
    
    def _generate_image_prompt(self) -> str:
        """Generate a detailed image prompt for this panel."""
        prompt_parts = [
            "Make a comic panel in the style of Amar Chitra Katha which shows:",
            self.scene_description
        ]
        
        if self.dialogue:
            prompt_parts.append(f"Include dialogue bubbles with: {'; '.join(self.dialogue)}")
        
        if self.narration:
            prompt_parts.append(f"Include narration text: {self.narration}")
        
        return " ".join(prompt_parts)