import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API key from environment
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


def get_gemini_model():
    """Returns an active GenerativeModel instance with fallback options."""
    api_key_current = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key_current and api_key_current != "your_gemini_api_key_here":
        genai.configure(api_key=api_key_current)
    
    # Try preferred models in order
    for m in ["models/gemini-1.5-pro", "gemini-1.5-pro", "models/gemini-1.5-flash", "gemini-1.5-flash", "gemini-pro"]:
        try:
            return genai.GenerativeModel(model_name=m)
        except Exception:
            continue
    return genai.GenerativeModel(model_name="models/gemini-1.5-pro")


def answer_question_with_gemini(question: str) -> str:
    try:
        api_key_current = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key_current or api_key_current == "your_gemini_api_key_here":
            return "⚠️ Gemini API Key not set. Please set GEMINI_API_KEY in the .env file."

        model = get_gemini_model()
        response = model.generate_content(question)
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        elif hasattr(response, "parts") and response.parts:
            return response.parts[0].text.strip()
        return "⚠️ Could not retrieve answer from model response."
    except Exception as e:
        return f"⚠️ Error in QnA: {e}"
