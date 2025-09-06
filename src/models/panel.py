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
    style: str = "amar_chitra_katha"
    
    def __post_init__(self):
        """Generate image prompt from panel details if not provided."""
        if not self.image_prompt:
            self.image_prompt = self._generate_image_prompt()
    
    def _generate_image_prompt(self) -> str:
        """Generate a detailed image prompt for this panel."""
        prompt_parts = [
            f"This is the design philosophy of my comics. Using this style as a metric, make me the following panel:",
            f"Panel {self.panel_number} - {self.scene_description}"
        ]
        
        if self.dialogue:
            for dialogue_line in self.dialogue:
                prompt_parts.append(f"Speech Bubble: {dialogue_line}")
        
        if self.narration:
            prompt_parts.append(f"Caption: {self.narration}")
        
        return " ".join(prompt_parts)