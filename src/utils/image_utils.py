from typing import Tuple, Optional

try:
    from PIL import Image, ImageDraw, ImageFont
    from IPython.display import display, Markdown, Image as IPImage
    PIL_AVAILABLE = True
    IPYTHON_AVAILABLE = True
except ImportError as e:
    PIL_AVAILABLE = False
    IPYTHON_AVAILABLE = False
    _missing_modules = str(e)


def display_response(response) -> None:
    """
    Display a response from Google GenAI, showing both text and images.
    
    Args:
        response: GenAI response object with parts
    """
    if not IPYTHON_AVAILABLE:
        print("IPython not available. Cannot display rich content.")
        return
    
    if not hasattr(response, 'parts') or not response.parts:
        print("No response parts to display")
        return
    
    for part in response.parts:
        if part.text:
            display(Markdown(part.text))
        elif image := part.as_image():
            display(image)


def save_image_from_response(response, output_path: str) -> bool:
    """
    Save the first image found in a response to the specified path.
    
    Args:
        response: GenAI response object
        output_path: Path where to save the image
        
    Returns:
        True if image was saved, False otherwise
    """
    if not hasattr(response, 'parts') or not response.parts:
        return False
    
    for part in response.parts:
        if image := part.as_image():
            image.save(output_path)
            return True
    
    return False


def resize_image(image_path: str, target_size: Tuple[int, int], output_path: Optional[str] = None) -> str:
    """
    Resize an image to target dimensions.
    
    Args:
        image_path: Path to the source image
        target_size: Target (width, height) tuple
        output_path: Optional output path, defaults to overwriting source
        
    Returns:
        Path to the resized image
        
    Raises:
        ImportError: If PIL is not available
    """
    if not PIL_AVAILABLE:
        raise ImportError("PIL (Pillow) is required for image resizing")
    
    output_path = output_path or image_path
    
    with Image.open(image_path) as img:
        resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
        resized_img.save(output_path, quality=95)
    
    return output_path


def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """
    Get the dimensions of an image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple of (width, height)
        
    Raises:
        ImportError: If PIL is not available
    """
    if not PIL_AVAILABLE:
        raise ImportError("PIL (Pillow) is required for image operations")
    
    with Image.open(image_path) as img:
        return img.size


def create_image_grid(image_paths: list[str], output_path: str, cols: int = 2, padding: int = 10) -> str:
    """
    Create a grid layout from multiple images.
    
    Args:
        image_paths: List of image file paths
        output_path: Path for the output grid image
        cols: Number of columns in the grid
        padding: Padding between images in pixels
        
    Returns:
        Path to the created grid image
        
    Raises:
        ImportError: If PIL is not available
    """
    if not PIL_AVAILABLE:
        raise ImportError("PIL (Pillow) is required for image grid creation")
    
    if not image_paths:
        raise ValueError("No images provided")
    
    # Load all images
    images = [Image.open(path) for path in image_paths]
    
    # Calculate grid dimensions
    rows = (len(images) + cols - 1) // cols
    
    # Find maximum dimensions
    max_width = max(img.width for img in images)
    max_height = max(img.height for img in images)
    
    # Calculate grid size
    grid_width = cols * max_width + (cols + 1) * padding
    grid_height = rows * max_height + (rows + 1) * padding
    
    # Create grid image
    grid_img = Image.new('RGB', (grid_width, grid_height), 'white')
    
    # Place images in grid
    for i, img in enumerate(images):
        row = i // cols
        col = i % cols
        
        x = col * max_width + (col + 1) * padding
        y = row * max_height + (row + 1) * padding
        
        # Resize image to fit grid cell
        resized_img = img.resize((max_width, max_height), Image.Resampling.LANCZOS)
        grid_img.paste(resized_img, (x, y))
    
    # Save grid
    grid_img.save(output_path, 'PNG', quality=95)
    
    # Close images
    for img in images:
        img.close()
    
    return output_path


def add_text_to_image(image_path: str, text: str, position: Tuple[int, int], 
                     output_path: Optional[str] = None, font_size: int = 24) -> str:
    """
    Add text overlay to an image.
    
    Args:
        image_path: Path to the source image
        text: Text to add
        position: (x, y) position for the text
        output_path: Optional output path, defaults to overwriting source
        font_size: Size of the font
        
    Returns:
        Path to the modified image
        
    Raises:
        ImportError: If PIL is not available
    """
    if not PIL_AVAILABLE:
        raise ImportError("PIL (Pillow) is required for text overlay")
    
    output_path = output_path or image_path
    
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()
        
        # Add text with black color
        draw.text(position, text, font=font, fill='black')
        
        img.save(output_path)
    
    return output_path