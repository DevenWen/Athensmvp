import pytest
from src.config.settings import settings
from src.core.ai_client import AIClient

def test_settings_load():
    """
    Tests if the application settings are loaded correctly.
    Assumes .env.example is copied to .env and API key is set for a real test,
    but for now, we just check if the object exists.
    """
    assert settings is not None
    # We can't assert openrouter_api_key because it would be None without a .env file
    # but we can check the defaults
    assert settings.default_model == "google/gemini-2.5-flash"

def test_ai_client_initialization():
    """
    Tests if the AIClient can be initialized.
    This test will fail if the OPENROUTER_API_KEY is not set in the environment.
    """
    # To run this test, create a .env file from .env.example and add a dummy key
    if not settings.openrouter_api_key:
        pytest.skip("OPENROUTER_API_KEY not set in environment, skipping client initialization test.")

    try:
        client = AIClient()
        assert client is not None
        assert client.model == settings.default_model
    except Exception as e:
        pytest.fail(f"AIClient initialization failed: {e}")
