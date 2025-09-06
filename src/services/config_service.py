import os
from typing import Optional
from dotenv import load_dotenv


class ConfigService:
    """Service for managing application configuration and API keys."""
    
    def __init__(self, env_file: str = ".env"):
        """Initialize configuration service and load environment variables."""
        self.env_file = env_file
        load_dotenv(self.env_file)
        self._validate_config()
    
    def _validate_config(self):
        """Validate that required configuration is present."""
        api_key = self.get_google_api_key()
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables. "
                "Please ensure it's set in your .env file."
            )
    
    def get_google_api_key(self) -> Optional[str]:
        """Get the Google GenAI API key from environment variables."""
        return os.getenv("GOOGLE_API_KEY")
    
    def get_model_id(self) -> str:
        """Get the model ID to use for generation."""
        return os.getenv("MODEL_ID", "gemini-2.5-flash-image-preview")
    
    def get_output_directory(self) -> str:
        """Get the directory for output files."""
        return os.getenv("OUTPUT_DIR", "output")
    
    def get_comic_style(self) -> str:
        """Get the default comic style."""
        return os.getenv("COMIC_STYLE", "amar_chitra_katha")
    
    @property
    def is_configured(self) -> bool:
        """Check if the service is properly configured."""
        try:
            self._validate_config()
            return True
        except ValueError:
            return False