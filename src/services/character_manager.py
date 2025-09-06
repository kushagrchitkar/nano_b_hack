import json
import os
import re
from typing import List, Dict
from ..models.character import Character
from ..models.script import Script
from ..models.panel import Panel


class CharacterManagerService:
    """Service for managing character consistency across comic panels."""
    
    def __init__(self, characters_file: str = "characters.json"):
        """Initialize the character manager."""
        self.characters_file = characters_file
        self.characters_cache: Dict[str, Character] = {}
    
    def extract_characters_from_script(self, script: Script) -> None:
        """Extract and register characters from dialogue in script panels."""
        for panel in script.panels:
            # Extract character names only from dialogue (speakers)
            character_names = self._extract_character_names_from_dialogue(panel.dialogue)
            
            # Remove duplicates and clean up
            character_names = list(set([name.title() for name in character_names if name]))
            
            # Add characters to panel and script
            for char_name in character_names:
                panel.add_character(char_name)
                
                # Create or update character
                character = self._get_or_create_character(char_name, panel.scene_description)
                character.add_appearance(panel.panel_number)
                script.add_character(character)
    
    def _extract_character_names_from_dialogue(self, dialogue: List[str]) -> List[str]:
        """Extract character names from dialogue lines."""
        character_names = []
        
        for line in dialogue:
            # Look for dialogue format like "Character: dialogue text"
            match = re.match(r'^([A-Za-z\s]+):\s*(.+)', line.strip())
            if match:
                character_name = match.group(1).strip()
                if character_name and len(character_name) > 1:
                    character_names.append(character_name)
        
        return character_names
    
    
    def _get_or_create_character(self, name: str, context: str = "") -> Character:
        """Get existing character or create new one with basic description."""
        name_key = name.lower()
        
        if name_key in self.characters_cache:
            return self.characters_cache[name_key]
        
        # Create new character with basic description
        description = self._generate_character_description(name, context)
        character = Character(name=name, visual_description=description)
        
        self.characters_cache[name_key] = character
        return character
    
    def _generate_character_description(self, name: str, context: str = "") -> str:
        """Generate a basic character description from context."""
        # This is a simple implementation - could be enhanced with AI
        description_parts = [f"Character named {name}"]
        
        if context:
            # Extract descriptive words from context
            descriptive_words = []
            context_lower = context.lower()
            
            # Look for age-related terms
            age_terms = ['young', 'old', 'elderly', 'child', 'boy', 'girl', 'man', 'woman']
            for term in age_terms:
                if term in context_lower:
                    descriptive_words.append(term)
            
            # Look for appearance terms
            appearance_terms = ['tall', 'short', 'thin', 'heavy', 'beard', 'mustache', 'long hair', 'bald']
            for term in appearance_terms:
                if term in context_lower:
                    descriptive_words.append(term)
            
            if descriptive_words:
                description_parts.append(f"described as {', '.join(descriptive_words)}")
        
        return ". ".join(description_parts)
    
    def update_character_description(self, name: str, description: str) -> None:
        """Update a character's visual description."""
        name_key = name.lower()
        if name_key in self.characters_cache:
            self.characters_cache[name_key].visual_description = description
    
    def get_character_descriptions(self, script: Script) -> Dict[str, str]:
        """Get character descriptions for all characters in a script."""
        descriptions = {}
        for character in script.characters:
            descriptions[character.name] = character.visual_description
        return descriptions
    
    def determine_reference_panels(self, panel: Panel, script: Script) -> List[int]:
        """Determine which panels to use as visual references for the current panel."""
        reference_panels = []
        
        # Strategy 1: Include previous 1-2 panels for scene continuity
        if panel.panel_number > 1:
            reference_panels.append(panel.panel_number - 1)
        if panel.panel_number > 2:
            reference_panels.append(panel.panel_number - 2)
        
        # Strategy 2: Include first appearance of characters in this panel
        for character_name in panel.characters_in_panel:
            char_references = script.get_character_reference_panels(character_name)
            for ref_panel in char_references:
                if ref_panel < panel.panel_number and ref_panel not in reference_panels:
                    reference_panels.append(ref_panel)
                    break  # Only add the first reference to avoid too many
        
        # Limit total references to avoid overwhelming the AI
        reference_panels.sort()
        return reference_panels[:4]  # Max 4 reference panels
    
    def save_characters(self) -> None:
        """Save characters to JSON file."""
        characters_data = {}
        for character in self.characters_cache.values():
            characters_data[character.name] = {
                'name': character.name,
                'visual_description': character.visual_description,
                'reference_panels': character.reference_panels,
                'first_appearance_panel': character.first_appearance_panel
            }
        
        with open(self.characters_file, 'w') as f:
            json.dump(characters_data, f, indent=2)
    
    def load_characters(self) -> None:
        """Load characters from JSON file."""
        if not os.path.exists(self.characters_file):
            return
        
        try:
            with open(self.characters_file, 'r') as f:
                characters_data = json.load(f)
            
            self.characters_cache = {}
            for char_data in characters_data.values():
                character = Character(
                    name=char_data['name'],
                    visual_description=char_data['visual_description'],
                    reference_panels=char_data.get('reference_panels', []),
                    first_appearance_panel=char_data.get('first_appearance_panel')
                )
                self.characters_cache[char_data['name'].lower()] = character
                
        except Exception as e:
            print(f"Warning: Could not load characters from {self.characters_file}: {e}")