import os
from typing import Tuple
from ..models.script import Script
from ..models.comic import Comic
from .config_service import ConfigService

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ComicAssemblerService:
    """Service for assembling individual panel images into a complete comic."""
    
    def __init__(self, config_service: ConfigService):
        """Initialize the comic assembler with configuration."""
        self.config = config_service
        self.output_dir = self.config.get_output_directory()
        
        if not PIL_AVAILABLE:
            raise ImportError(
                "PIL (Pillow) is required for comic assembly. "
                "Install it with: pip install Pillow"
            )
    
    def assemble_comic(self, script: Script) -> Comic:
        """
        Assemble a complete comic from a script with generated panel images.
        
        Args:
            script: Script object with panels that have image_path set
            
        Returns:
            Comic object with assembled comic path
        """
        if not self._all_panels_have_images(script):
            raise ValueError("Not all panels have generated images")
        
        # Generate output filename
        safe_title = self._sanitize_filename(script.title)
        output_filename = f"{safe_title}_complete_comic.png"
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Create the comic layout
        self._create_comic_layout(script, output_path)
        
        return Comic(
            script=script,
            output_path=output_path
        )
    
    def _all_panels_have_images(self, script: Script) -> bool:
        """Check if all panels in the script have generated images."""
        return all(
            panel.image_path and os.path.exists(panel.image_path) 
            for panel in script.panels
        )
    
    def _create_comic_layout(self, script: Script, output_path: str):
        """Create the actual comic layout by arranging panel images."""
        panel_images = [Image.open(panel.image_path) for panel in script.panels]
        
        # Determine layout (2 columns for most cases)
        cols = 2
        rows = (len(panel_images) + cols - 1) // cols
        
        # Calculate dimensions
        panel_width = max(img.width for img in panel_images)
        panel_height = max(img.height for img in panel_images)
        
        # Add padding
        padding = 20
        title_height = 100
        
        comic_width = cols * panel_width + (cols + 1) * padding
        comic_height = rows * panel_height + (rows + 1) * padding + title_height
        
        # Create the composite image
        comic_image = Image.new('RGB', (comic_width, comic_height), 'white')
        draw = ImageDraw.Draw(comic_image)
        
        # Add title
        self._add_title(draw, script.title, comic_width, title_height)
        
        # Arrange panels
        for i, (panel, img) in enumerate(zip(script.panels, panel_images)):
            row = i // cols
            col = i % cols
            
            x = col * panel_width + (col + 1) * padding
            y = row * panel_height + (row + 1) * padding + title_height
            
            # Resize panel image to standard size
            resized_img = img.resize((panel_width, panel_height), Image.Resampling.LANCZOS)
            comic_image.paste(resized_img, (x, y))
            
            # Add panel border
            draw.rectangle([x-2, y-2, x + panel_width + 2, y + panel_height + 2], 
                         outline='black', width=2)
        
        # Save the assembled comic
        comic_image.save(output_path, 'PNG', quality=95)
    
    def _add_title(self, draw: ImageDraw.Draw, title: str, width: int, height: int):
        """Add title text to the comic."""
        try:
            # Try to use a larger font
            font = ImageFont.truetype("arial.ttf", 36)
        except (OSError, IOError):
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Calculate text position (centered)
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), title, font=font, fill='black')
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a string to be safe for use as a filename."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        filename = '_'.join(filename.split())
        return filename[:50] if len(filename) > 50 else filename