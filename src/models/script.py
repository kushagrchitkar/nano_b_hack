from dataclasses import dataclass
from typing import List
from .panel import Panel


@dataclass
class Script:
    """Represents a complete comic script with multiple panels and metadata."""
    
    title: str
    event_description: str
    panels: List[Panel]
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