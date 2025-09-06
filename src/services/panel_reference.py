import os
from typing import List, Optional
from ..models.panel import Panel
from ..models.script import Script

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class PanelReferenceManager:
    """Manages visual references from previously generated panels."""
    
    def __init__(self, output_dir: str):
        """Initialize with the directory containing generated panel images."""
        self.output_dir = output_dir
        
        if not PIL_AVAILABLE:
            print("Warning: PIL not available. Visual panel references may not work.")
    
    def get_reference_images(self, reference_panels: List[int], comic_title: str) -> List[PILImage.Image]:
        """Load reference panel images for visual consistency."""
        if not PIL_AVAILABLE:
            return []
        
        reference_images = []
        
        for panel_number in reference_panels:
            image_path = self._get_panel_image_path(panel_number, comic_title)
            if image_path and os.path.exists(image_path):
                try:
                    image = PILImage.open(image_path)
                    reference_images.append(image)
                except Exception as e:
                    print(f"Warning: Could not load reference panel {panel_number}: {e}")
        
        return reference_images
    
    def _get_panel_image_path(self, panel_number: int, comic_title: str) -> Optional[str]:
        """Get the file path for a specific panel image."""
        safe_title = self._sanitize_filename(comic_title)
        filename = f"{safe_title}_panel_{panel_number:02d}.png"
        return os.path.join(self.output_dir, filename)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a string to be safe for use as a filename."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        filename = '_'.join(filename.split())
        return filename[:50] if len(filename) > 50 else filename
    
    def build_visual_references(self, panel: Panel, script: Script, character_manager) -> List[PILImage.Image]:
        """Build comprehensive visual references for a panel."""
        if not PIL_AVAILABLE:
            return []
        
        # Get reference panel numbers
        reference_panels = character_manager.determine_reference_panels(panel, script)
        panel.set_reference_panels(reference_panels)
        
        # Load reference images
        reference_images = self.get_reference_images(reference_panels, script.title)
        
        return reference_images
    
    def create_reference_context_prompt(self, reference_panels: List[int]) -> str:
        """Create a text prompt explaining the visual references being provided."""
        if not reference_panels:
            return ""
        
        if len(reference_panels) == 1:
            return f"Use the reference image from panel {reference_panels[0]} to maintain visual consistency for characters and style."
        else:
            panel_list = ", ".join([str(p) for p in reference_panels[:-1]])
            return f"Use the reference images from panels {panel_list} and {reference_panels[-1]} to maintain visual consistency for characters and style."