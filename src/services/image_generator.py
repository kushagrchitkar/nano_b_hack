import os
from typing import Optional
from google import genai
from google.genai import types
from ..models.panel import Panel
from .config_service import ConfigService


class ImageGeneratorService:
    """Service for generating images for comic panels."""
    
    def __init__(self, config_service: ConfigService):
        """Initialize the image generator with configuration."""
        self.config = config_service
        self.client = genai.Client(api_key=self.config.get_google_api_key())
        self.output_dir = self.config.get_output_directory()
        self._ensure_output_directory()
    
    def _ensure_output_directory(self):
        """Ensure the output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_panel_image(self, panel: Panel, comic_title: str) -> str:
        """
        Generate an image for a specific panel.
        
        Args:
            panel: Panel object with scene description and details
            comic_title: Title of the comic for filename generation
            
        Returns:
            Path to the generated image file
        """
        try:
            response = self.client.models.generate_content(
                model=self.config.get_model_id(),
                contents=panel.image_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
            
            # Generate filename
            safe_title = self._sanitize_filename(comic_title)
            filename = f"{safe_title}_panel_{panel.panel_number:02d}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save image from response
            self._save_image_from_response(response, filepath)
            
            # Update panel with image path
            panel.image_path = filepath
            
            return filepath
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate image for panel {panel.panel_number}: {str(e)}")
    
    def _save_image_from_response(self, response, filepath: str):
        """Save the image from the response to the specified filepath."""
        if not response.parts:
            raise ValueError("No response parts found")
        
        image_saved = False
        for part in response.parts:
            if image := part.as_image():
                image.save(filepath)
                image_saved = True
                break
        
        if not image_saved:
            raise ValueError("No image found in response")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a string to be safe for use as a filename."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove extra spaces and limit length
        filename = '_'.join(filename.split())
        return filename[:50] if len(filename) > 50 else filename
    
    def generate_all_panel_images(self, script, progress_callback: Optional[callable] = None) -> list[str]:
        """
        Generate images for all panels in a script.
        
        Args:
            script: Script object with panels
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of image file paths
        """
        image_paths = []
        
        for i, panel in enumerate(script.panels):
            try:
                if progress_callback:
                    progress_callback(f"Generating image for panel {panel.panel_number}...")
                
                filepath = self.generate_panel_image(panel, script.title)
                image_paths.append(filepath)
                
                if progress_callback:
                    progress_callback(f"✅ Panel {panel.panel_number} image saved: {filepath}")
                    
            except Exception as e:
                error_msg = f"❌ Failed to generate panel {panel.panel_number}: {e}"
                if progress_callback:
                    progress_callback(error_msg)
                else:
                    print(error_msg)
        
        return image_paths