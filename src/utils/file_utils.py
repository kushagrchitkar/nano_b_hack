import os
import json
from typing import Any, Dict
from datetime import datetime


def ensure_directory(directory_path: str) -> None:
    """Ensure a directory exists, creating it if necessary."""
    os.makedirs(directory_path, exist_ok=True)


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize a filename by removing invalid characters and limiting length.
    
    Args:
        filename: Raw filename string
        max_length: Maximum length for the filename
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Replace multiple spaces/underscores with single underscore
    filename = '_'.join(filename.split())
    
    # Limit length while preserving extension
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        max_name_length = max_length - len(ext)
        filename = name[:max_name_length] + ext
    
    return filename


def save_json(data: Dict[str, Any], filepath: str) -> None:
    """Save data as JSON to a file."""
    ensure_directory(os.path.dirname(filepath))
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def load_json(filepath: str) -> Dict[str, Any]:
    """Load JSON data from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_unique_filename(base_path: str, extension: str = "") -> str:
    """
    Generate a unique filename by adding a counter if the file exists.
    
    Args:
        base_path: Base file path without extension
        extension: File extension (with or without dot)
        
    Returns:
        Unique file path
    """
    if extension and not extension.startswith('.'):
        extension = '.' + extension
    
    counter = 0
    while True:
        if counter == 0:
            filepath = base_path + extension
        else:
            filepath = f"{base_path}_{counter}{extension}"
        
        if not os.path.exists(filepath):
            return filepath
        
        counter += 1


def get_file_age_hours(filepath: str) -> float:
    """Get the age of a file in hours."""
    if not os.path.exists(filepath):
        return float('inf')
    
    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
    current_time = datetime.now()
    age_delta = current_time - file_time
    
    return age_delta.total_seconds() / 3600