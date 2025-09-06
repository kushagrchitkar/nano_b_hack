#!/usr/bin/env python3
"""
Comic Generation System - Main Application

A system that generates comics from event descriptions using AI.
Takes an event description, generates a script, creates images for each panel,
and assembles them into a complete comic.
"""

import sys
import argparse
from typing import Optional

from src.services.config_service import ConfigService
from src.services.script_generator import ScriptGeneratorService
from src.services.script_parser import ScriptParserService
from src.services.image_generator import ImageGeneratorService
from src.services.comic_assembler import ComicAssemblerService
from src.utils.image_utils import display_response


class ComicGenerator:
    """Main application class for comic generation."""
    
    def __init__(self):
        """Initialize the comic generator with all required services."""
        try:
            self.config = ConfigService()
            self.script_generator = ScriptGeneratorService(self.config)
            self.script_parser = ScriptParserService()
            self.image_generator = ImageGeneratorService(self.config)
            self.comic_assembler = ComicAssemblerService(self.config)
            
        except Exception as e:
            print(f"❌ Failed to initialize comic generator: {e}")
            sys.exit(1)
    
    def generate_comic(self, event_description: str, style: Optional[str] = None) -> str:
        """
        Generate a complete comic from an event description.
        
        Args:
            event_description: Description of the event to create a comic about
            style: Optional comic style (defaults to config setting)
            
        Returns:
            Path to the generated comic file
        """
        print(f"🎬 Starting comic generation for: {event_description}")
        
        try:
            # Step 1: Generate script
            print("\n📝 Generating comic script...")
            script_text = self.script_generator.generate_script(event_description, style)
            print("✅ Script generated successfully!")
            
            # Step 2: Parse script into panels
            print("\n🎯 Parsing script into panels...")
            script = self.script_parser.parse_script(script_text, event_description)
            print(f"✅ Parsed {script.panel_count} panels")
            
            # Display script info
            print(f"📖 Comic Title: {script.title}")
            for panel in script.panels:
                print(f"   Panel {panel.panel_number}: {panel.scene_description[:50]}...")
            
            # Step 3: Generate images for all panels
            print(f"\n🎨 Generating images for {script.panel_count} panels...")
            self.image_generator.generate_all_panel_images(
                script, 
                progress_callback=lambda msg: print(f"   {msg}")
            )
            
            # Step 4: Assemble final comic
            print("\n🎭 Assembling final comic...")
            comic = self.comic_assembler.assemble_comic(script)
            print(f"✅ Comic assembled: {comic.output_path}")
            
            return comic.output_path
            
        except Exception as e:
            print(f"❌ Error generating comic: {e}")
            raise
    
    def quick_test(self):
        """Quick test to verify the system works with a simple example."""
        print("🧪 Running quick test...")
        
        test_event = "birth of Alexander the Great"
        try:
            comic_path = self.generate_comic(test_event)
            print(f"\n🎉 Test completed successfully!")
            print(f"📁 Comic saved to: {comic_path}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate comics from event descriptions using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "birth of Alexander the Great"
  %(prog)s "discovery of fire" --style amar_chitra_katha
  %(prog)s --test
        """
    )
    
    parser.add_argument(
        "event",
        nargs="?",
        help="Description of the historical event or story to create a comic about"
    )
    
    parser.add_argument(
        "--style",
        help="Comic style (default: amar_chitra_katha)",
        default=None
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run a quick test with a predefined example"
    )
    
    args = parser.parse_args()
    
    # Initialize the generator
    generator = ComicGenerator()
    
    if args.test:
        generator.quick_test()
        return
    
    if not args.event:
        print("❌ Error: Please provide an event description or use --test")
        parser.print_help()
        sys.exit(1)
    
    try:
        comic_path = generator.generate_comic(args.event, args.style)
        print(f"\n🎉 Comic generation completed!")
        print(f"📁 Your comic is saved at: {comic_path}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Comic generation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to generate comic: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()