# Legacy utils wrapper - for backward compatibility
from src.utils.image_utils import display_response, save_image_from_response

def save_image(response, path):
    """Legacy wrapper for save_image_from_response."""
    return save_image_from_response(response, path)