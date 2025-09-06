from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from .script import Script


@dataclass
class Comic:
    """Represents a final assembled comic with images and layout."""
    
    script: Script
    output_path: str
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set creation time if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def title(self) -> str:
        """Get the comic title from the script."""
        return self.script.title
    
    @property
    def panel_count(self) -> int:
        """Get the total number of panels in this comic."""
        return self.script.panel_count
    
    @property
    def has_all_images(self) -> bool:
        """Check if all panels have generated images."""
        return all(panel.image_path is not None for panel in self.script.panels)