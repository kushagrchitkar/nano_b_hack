import re
from typing import List, Optional
from ..models.panel import Panel
from ..models.script import Script


class ScriptParserService:
    """Service for parsing generated script text into structured Panel and Script objects."""
    
    def parse_script(self, script_text: str, event_description: str, style: str = "amar_chitra_katha") -> Script:
        """
        Parse script text into a Script object with Panel instances.
        
        Args:
            script_text: Raw script text from generator
            event_description: Original event description
            style: Comic style for image generation
            
        Returns:
            Parsed Script object
        """
        title = self._extract_title(script_text)
        panels = self._extract_panels(script_text, style)
        
        return Script(
            title=title,
            event_description=event_description,
            panels=panels,
            style=style
        )
    
    def _extract_title(self, script_text: str) -> str:
        """Extract the comic title from script text."""
        title_match = re.search(r'TITLE:\s*(.+)', script_text, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        
        # Fallback to first line if no TITLE: found
        first_line = script_text.split('\n')[0].strip()
        if first_line and not first_line.startswith('PANEL'):
            return first_line
        
        return "Untitled Comic"
    
    def _extract_panels(self, script_text: str, style: str) -> List[Panel]:
        """Extract all panels from the script text."""
        panels = []
        
        # Find all PANEL sections using findall
        panel_matches = re.findall(r'PANEL\s+(\d+):(.*?)(?=PANEL\s+\d+:|$)', script_text, re.IGNORECASE | re.DOTALL)
        
        for panel_number_str, panel_content in panel_matches:
            panel_number = int(panel_number_str)
            panel = self._parse_panel_content(panel_number, panel_content, style)
            if panel:
                panels.append(panel)
        
        return panels
    
    def _parse_panel_content(self, panel_number: int, content: str, style: str) -> Optional[Panel]:
        """Parse individual panel content into a Panel object."""
        try:
            scene_description = self._extract_scene(content)
            dialogue = self._extract_dialogue(content)
            narration = self._extract_narration(content)
            
            if not scene_description:
                return None
            
            return Panel(
                panel_number=panel_number,
                scene_description=scene_description,
                dialogue=dialogue,
                narration=narration,
                style=style
            )
            
        except Exception as e:
            print(f"Warning: Failed to parse panel {panel_number}: {e}")
            return None
    
    def _extract_scene(self, content: str) -> str:
        """Extract scene description from panel content."""
        scene_match = re.search(r'SCENE:\s*(.+?)(?=DIALOGUE:|NARRATION:|PANEL|\Z)', 
                               content, re.IGNORECASE | re.DOTALL)
        if scene_match:
            return scene_match.group(1).strip()
        
        return ""
    
    def _extract_dialogue(self, content: str) -> List[str]:
        """Extract dialogue lines from panel content."""
        dialogue_section = re.search(r'DIALOGUE:\s*(.+?)(?=NARRATION:|PANEL|\Z)', 
                                    content, re.IGNORECASE | re.DOTALL)
        
        if not dialogue_section:
            return []
        
        dialogue_text = dialogue_section.group(1).strip()
        if not dialogue_text or dialogue_text.lower() in ['[none]', 'none']:
            return []
        
        # Split dialogue into individual lines and clean them
        lines = [line.strip() for line in dialogue_text.split('\n') if line.strip()]
        # Filter out empty lines and extract actual dialogue
        dialogue_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('['):
                # If line contains a character name followed by colon, it's dialogue
                if ':' in line and not line.lower().startswith('dialogue'):
                    dialogue_lines.append(line)
                # Otherwise, if it's not a section header, include it too
                elif not line.upper().startswith(('SCENE', 'DIALOGUE', 'NARRATION')):
                    dialogue_lines.append(line)
        
        return dialogue_lines
    
    def _extract_narration(self, content: str) -> Optional[str]:
        """Extract narration text from panel content."""
        narration_match = re.search(r'NARRATION:\s*(.+?)(?=PANEL|\Z)', 
                                   content, re.IGNORECASE | re.DOTALL)
        
        if narration_match:
            narration = narration_match.group(1).strip()
            if narration and narration.lower() not in ['[none]', 'none']:
                return narration
        
        return None