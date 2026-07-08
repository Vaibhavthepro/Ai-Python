import os
import google.generativeai as genai
from dotenv import load_dotenv

class AIHelper:
    def __init__(self):
        # Load environment variables
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        load_dotenv(dotenv_path)
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            # Use gemini-1.5-flash as it's fast
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def explain_error(self, error_type: str, error_msg: str, traceback: str) -> dict:
        if not self.model:
            return {"explanation": "AI is not configured. GEMINI_API_KEY is missing.", "fix": ""}

        prompt = f"""
An error occurred in a Python script.
Error Type: {error_type}
Error Message: {error_msg}
Traceback:
{traceback}

Provide a concise explanation of why this error happened.
Then, provide a possible short code snippet to fix it.
Respond EXACTLY in this format:
Explanation:
<your explanation here>

Possible Fix:
<your code fix here>
"""
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            
            parts = text.split("Possible Fix:")
            explanation = parts[0].replace("Explanation:", "").strip()
            fix = parts[1].strip() if len(parts) > 1 else ""
            
            return {"explanation": explanation, "fix": fix}
        except Exception as e:
            return {"explanation": f"AI failed to generate explanation: {str(e)}", "fix": ""}
