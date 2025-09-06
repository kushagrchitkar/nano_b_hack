import os
from typing import Optional, List
from google import genai
from google.genai import types
from ..models.panel import Panel
from ..models.script import Script
from .config_service import ConfigService
from .character_manager import CharacterManagerService
from .panel_reference import PanelReferenceManager

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ImageGeneratorService:
    """Service for generating images for comic panels."""
    
    def __init__(self, config_service: ConfigService):
        """Initialize the image generator with configuration."""
        self.config = config_service
        self.client = genai.Client(api_key=self.config.get_google_api_key())
        self.output_dir = self.config.get_output_directory()
        self.design_philosophy_dir = "design_philosophy"
        self.character_manager = CharacterManagerService()
        self.panel_reference_manager = PanelReferenceManager(self.output_dir)
        self._ensure_output_directory()
        
        if not PIL_AVAILABLE:
            print("Warning: PIL not available. Image-based style references may not work.")
    
    def _ensure_output_directory(self):
        """Ensure the output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _get_style_reference_image(self, style: str) -> Optional[PILImage.Image]:
        """Get the reference image for a given style."""
        if not PIL_AVAILABLE:
            return None
        
        # Normalize style name and look for reference image
        style_filename = f"{style.lower()}.jpg"
        style_path = os.path.join(self.design_philosophy_dir, style_filename)
        
        if os.path.exists(style_path):
            try:
                return PILImage.open(style_path)
            except Exception as e:
                print(f"Warning: Could not load style reference image {style_path}: {e}")
                return None
        else:
            print(f"Warning: No reference image found for style '{style}' at {style_path}")
            return None
    
    def generate_panel_image(self, panel: Panel, script: Script) -> str:
        """
        Generate an image for a specific panel with character consistency.
        
        Args:
            panel: Panel object with scene description and details
            script: Script object containing all panels and character info
            
        Returns:
            Path to the generated image file
        """
        try:
            # Get character descriptions for consistency
            character_descriptions = self.character_manager.get_character_descriptions(script)
            
            # Build visual references from previous panels
            reference_images = self.panel_reference_manager.build_visual_references(
                panel, script, self.character_manager
            )
            
            # Get style reference image
            style_image = self._get_style_reference_image(panel.style)
            
            # Build enhanced prompt with character descriptions
            enhanced_prompt = panel._generate_image_prompt(character_descriptions)
            
            # Add reference context if we have visual references
            if reference_images:
                reference_context = self.panel_reference_manager.create_reference_context_prompt(
                    panel.reference_panels
                )
                enhanced_prompt = f"{reference_context} {enhanced_prompt}"
            
            # Prepare contents for generation
            contents = [enhanced_prompt]
            
            # Add all reference images
            if style_image:
                contents.append(style_image)
            
            contents.extend(reference_images)
            
            response = self.client.models.generate_content(
                model=self.config.get_model_id(),
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
            
            # Generate filename
            safe_title = self._sanitize_filename(script.title)
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
        Generate images for all panels in a script with character consistency.
        
        Args:
            script: Script object with panels
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of image file paths
        """
        # Extract and process characters from the script
        if progress_callback:
            progress_callback("Extracting characters and building consistency data...")
        
        self.character_manager.load_characters()
        self.character_manager.extract_characters_from_script(script)
        
        image_paths = []
        
        for i, panel in enumerate(script.panels):
            try:
                if progress_callback:
                    progress_callback(f"Generating image for panel {panel.panel_number}...")
                
                filepath = self.generate_panel_image(panel, script)
                image_paths.append(filepath)
                
                if progress_callback:
                    progress_callback(f"✅ Panel {panel.panel_number} image saved: {filepath}")
                    
            except Exception as e:
                error_msg = f"❌ Failed to generate panel {panel.panel_number}: {e}"
                if progress_callback:
                    progress_callback(error_msg)
                else:
                    print(error_msg)
        
        # Save character data for future use
        self.character_manager.save_characters()
        
        return image_paths