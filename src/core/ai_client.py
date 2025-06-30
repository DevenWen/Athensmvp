import openai
from src.config.settings import settings

class AIClient:
    def __init__(self, model: str = None):
        self.model = model or settings.default_model
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )

    def generate_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1024):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
