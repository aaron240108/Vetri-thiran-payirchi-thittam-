import json
import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


def clean_json_block(text: str) -> str:
    """Remove Markdown ```json code fences and trim whitespace."""
    cleaned = re.sub(r"```(?:json)?\s*\n?(.*?)\s*```", r"\1", text, flags=re.DOTALL).strip()
    return cleaned


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


def generate_quiz(text: str) -> list:
    try:
        api_key_current = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key_current or api_key_current == "your_gemini_api_key_here":
            return [
                {
                    "question": "Sample Question (Configure GEMINI_API_KEY to generate dynamic AI quizzes): What is the key focus of EduGenie?",
                    "options": [
                        "Personalized learning with AI assistance",
                        "Playing video games",
                        "Weather forecasting only",
                        "Automobile manufacturing"
                    ],
                    "answer": "Personalized learning with AI assistance"
                }
            ]

        model = get_gemini_model()
        prompt = f"""
You are a quiz generator.

From the following passage, create 3 multiple-choice questions. Each question should include:
- A "question"
- A list of 4 "options"
- A correct "answer" that must exactly match one of the options.

Format your output as **valid JSON**, like this:
[
  {{
    "question": "What is ...?",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }}
]

Passage:
{text}
"""
        response = model.generate_content(prompt)
        quiz_text = response.text.strip() if hasattr(response, "text") and response.text else response.parts[0].text.strip()

        # Clean markdown code blocks if any
        cleaned_text = clean_json_block(quiz_text)

        # Extract JSON array substring if surrounding characters exist
        if "[" in cleaned_text and "]" in cleaned_text:
            cleaned_text = cleaned_text[cleaned_text.find("["):cleaned_text.rfind("]")+1]

        quiz_data = json.loads(cleaned_text)
        return quiz_data

    except Exception as e:
        print(f"Error in Quiz generation: {e}")
        return [{"error": f"⚠️ Error in Quiz: {e}"}]
