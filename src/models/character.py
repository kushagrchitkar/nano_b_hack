from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Character:
    """Represents a character in a comic with visual consistency tracking."""
    
    name: str
    visual_description: str
    reference_panels: List[int] = field(default_factory=list)
    first_appearance_panel: Optional[int] = None
    
    def add_appearance(self, panel_number: int):
        """Record that this character appears in a specific panel."""
        if self.first_appearance_panel is None:
            self.first_appearance_panel = panel_number
        
        if panel_number not in self.reference_panels:
            self.reference_panels.append(panel_number)
    
    def get_reference_panels(self, max_references: int = 3) -> List[int]:
        """Get the most relevant panel references for this character."""
        if not self.reference_panels:
            return []
        
        # Always include first appearance if available
        references = []
        if self.first_appearance_panel is not None:
            references.append(self.first_appearance_panel)
        
        # Add most recent appearances (excluding first if already added)
        recent_panels = [p for p in self.reference_panels if p != self.first_appearance_panel]
        recent_panels.sort(reverse=True)  # Most recent first
        
        # Add recent panels up to the limit
        for panel in recent_panels:
            if len(references) >= max_references:
                break
            references.append(panel)
        
        return sorted(references)