import google.generativeai as genai
import json
from app.domain.ports.ai_provider import IAIProvider, GeneratedCodeResponse
from app.core.config import settings

class GeminiAIAdapter(IAIProvider):
    def __init__(self, api_key: str = None, model_name: str = "gemini-2.5-flash"):
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(model_name)

    async def generate_code(self, prompt: str) -> GeneratedCodeResponse:
        system_instructions = (
            "You are a Python code generation engine. Respond ONLY with valid JSON "
            "matching exactly this schema: {\"code\": \"string\", \"explanation\": \"string\", \"imports\": [\"string\"]}. "
            "Do not include markdown fences or prose outside the JSON. Ensure the JSON is well-formed."
        )
        # Assuming the genai SDK is mostly sync, we can run it in a thread or use generate_content_async if available
        # The new SDK has generate_content_async
        response = await self.model.generate_content_async(
            contents=[system_instructions, prompt],
            # generation_config={"response_mime_type": "application/json"} # Sometimes causes issues if not fully supported, so we enforce it via prompt
        )
        
        # Cleanup response text to ensure it's just json (in case it includes markdown fences)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        return GeneratedCodeResponse(**data)
