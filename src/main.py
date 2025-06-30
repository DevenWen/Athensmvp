from src.core.ai_client import AIClient
from src.config.settings import settings

def main():
    """
    Main function to initialize and run the Athens MVP application.
    """
    print("Initializing Athens MVP...")
    print(f"Default model: {settings.default_model}")

    # Initialize the AI Client
    try:
        ai_client = AIClient()
        print("AI Client initialized successfully.")
        # A simple test to see if client can be used (requires API key)
        # print("Testing AI client connection...")
        # response = ai_client.generate_response("Hello, world!")
        # if response:
        #     print("AI Client test response received.")
        # else:
        #     print("AI Client test failed. Check API key and network.")
    except Exception as e:
        print(f"Error initializing AI Client: {e}")
        print("Please ensure your .env file is set up correctly with an OPENROUTER_API_KEY.")

    print("Athens MVP initialization complete.")

if __name__ == "__main__":
    main()
