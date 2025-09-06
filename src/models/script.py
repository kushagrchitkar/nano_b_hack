from dataclasses import dataclass, field
from typing import List
from .panel import Panel
from .character import Character


@dataclass
class Script:
    """Represents a complete comic script with multiple panels and metadata."""
    
    title: str
    event_description: str
    panels: List[Panel]
    characters: List[Character] = field(default_factory=list)
    style: str = "amar_chitra_katha"
    
    def __post_init__(self):
        """Ensure panels are numbered correctly."""
        for i, panel in enumerate(self.panels, 1):
            panel.panel_number = i
    
    @property
    def panel_count(self) -> int:
        """Get the total number of panels in this script."""
        return len(self.panels)
    
    def get_panel(self, panel_number: int) -> Panel:
        """Get a specific panel by number (1-indexed)."""
        if panel_number < 1 or panel_number > len(self.panels):
            raise ValueError(f"Panel number {panel_number} out of range. Script has {len(self.panels)} panels.")
        
        return self.panels[panel_number - 1]
    
    def add_character(self, character: Character) -> None:
        """Add a character to the script if not already present."""
        if not any(c.name == character.name for c in self.characters):
            self.characters.append(character)
    
    def get_character(self, name: str) -> Character:
        """Get a character by name."""
        for character in self.characters:
            if character.name.lower() == name.lower():
                return character
        raise ValueError(f"Character '{name}' not found in script")
    
    def get_panels_with_character(self, character_name: str) -> List[Panel]:
        """Get all panels where a specific character appears."""
        return [panel for panel in self.panels 
                if character_name.lower() in [char.lower() for char in panel.characters_in_panel]]
    
    def get_character_reference_panels(self, character_name: str) -> List[int]:
        """Get reference panel numbers for a character for visual consistency."""
        try:
            character = self.get_character(character_name)
            return character.get_reference_panels()
        except ValueError:
            return []