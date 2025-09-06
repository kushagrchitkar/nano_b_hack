import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from utils import display_response, save_image

MODEL_ID = "gemini-2.5-flash-image-preview"

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables")
        return
    
    # Initialize the client
    try:
        client = genai.Client(api_key=api_key)
        print("✅ Google GenAI client initialized successfully!")
        print(f"Client type: {type(client)}")
        
        # Generate comic
        prompt = 'Make a comic in the style of amar chitra katha which shows the event of birth of alexander the great along with relevant text and dialogue bubbles if necessary.'
        
        print("\n🎨 Generating comic...")
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )
        
        print("💾 Saving image...")
        save_image(response, 'alexander_comic.png')
        print("✅ Image saved as alexander_comic.png")
        
        print("\n📖 Response:")
        display_response(response)
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
