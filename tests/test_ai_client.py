import pytest
from src.config.settings import settings
from src.core.ai_client import AIClient


def test_ai_client_api_call():
    """
    测试 AIClient 能否成功调用 OpenRouter API
    验证基本的 generate_response 功能
    """
    if not settings.openrouter_api_key:
        pytest.skip("OPENROUTER_API_KEY not set in environment, skipping API test.")
    
    client = AIClient()
    
    # 使用简单的提示词测试API调用
    prompt = "Say hello in one word."
    response = client.generate_response(prompt, temperature=0.3, max_tokens=10)
    
    # 验证响应不为空
    assert response is not None
    assert isinstance(response, str)
    assert len(response.strip()) > 0
    
    print(f"API调用成功，响应: {response}")


def test_ai_client_initialization():
    """
    测试 AIClient 初始化
    """
    if not settings.openrouter_api_key:
        pytest.skip("OPENROUTER_API_KEY not set in environment, skipping initialization test.")
    
    # 测试默认模型初始化
    client = AIClient()
    assert client.model == settings.default_model
    
    # 测试自定义模型初始化
    custom_model = "openai/gpt-4"
    client_custom = AIClient(model=custom_model)
    assert client_custom.model == custom_model