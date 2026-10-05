import os
import traceback
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


def get_gemini_model():
    """Returns an active GenerativeModel instance with fallback options."""
    api_key_current = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key_current and api_key_current != "your_gemini_api_key_here":
        genai.configure(api_key=api_key_current)

    for m in ["models/gemini-1.5-pro", "gemini-1.5-pro", "models/gemini-1.5-flash", "gemini-1.5-flash", "gemini-pro"]:
        try:
            return genai.GenerativeModel(model_name=m)
        except Exception:
            continue
    return genai.GenerativeModel(model_name="models/gemini-1.5-pro")


def get_learning_recommendations(topic: str):
    prompt = f"""
You are an AI tutor. The student wants to learn about: {topic}.
Suggest a structured and adaptive learning path including key topics, order of learning, and resources (interactive tutorials, videos, books, online documentation, practice platforms). Include beginner, intermediate, and advanced levels if needed.
"""
    try:
        api_key_current = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key_current or api_key_current == "your_gemini_api_key_here":
            return "⚠️ Gemini API Key not set. Please set GEMINI_API_KEY in the .env file to generate learning recommendations."

        model = get_gemini_model()
        response = model.generate_content(prompt)
        print("🧠 Gemini raw response:", response)

        if hasattr(response, "text") and response.text:
            return response.text
        elif hasattr(response, "parts") and response.parts:
            return response.parts[0].text
        else:
            return "❌ Could not extract content from Gemini response."
    except Exception as e:
        traceback.print_exc()  # ✅ This gives full error trace
        return f"❌ Error occurred: {str(e)}"
