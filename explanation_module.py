import os
from dotenv import load_dotenv

load_dotenv()

explain_tokenizer = None
explain_model = None
_model_load_attempted = False


def _init_local_model():
    """Lazily load the LaMini-Flan-T5 model on first request to prevent blocking app startup."""
    global explain_tokenizer, explain_model, _model_load_attempted
    if _model_load_attempted:
        return explain_tokenizer, explain_model

    _model_load_attempted = True
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        import torch

        print("🔄 Loading local LaMini-Flan-T5-783M model...")
        explain_tokenizer = AutoTokenizer.from_pretrained("MBZUAI/LaMini-Flan-T5-783M")
        explain_model = AutoModelForSeq2SeqLM.from_pretrained("MBZUAI/LaMini-Flan-T5-783M")
        print("✅ Local LaMini-Flan-T5-783M model loaded successfully.")
    except Exception as e:
        print(f"ℹ️ Note: Local transformers model not loaded ({e}). Using AI API fallback.")
        explain_tokenizer = None
        explain_model = None

    return explain_tokenizer, explain_model


def explain_topic(topic: str) -> str:
    """Explains a topic in a simple and clear way for a school student."""
    try:
        tokenizer, model = _init_local_model()
        if tokenizer is not None and model is not None:
            input_text = f"Explain the concept of '{topic}' in a simple and clear way for a school student."
            inputs = tokenizer(input_text, return_tensors="pt")

            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
                do_sample=True,
            )

            explanation = tokenizer.decode(outputs[0], skip_special_tokens=True)
            return explanation
        else:
            # Fallback using Gemini with the exact school student explanation prompt
            import google.generativeai as genai

            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key and api_key != "your_gemini_api_key_here":
                genai.configure(api_key=api_key)
                for m_name in ["models/gemini-1.5-pro", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]:
                    try:
                        g_model = genai.GenerativeModel(model_name=m_name)
                        prompt = f"Explain the concept of '{topic}' in a simple and clear way for a school student. Keep it concise, accessible, and structured (around 100-150 words)."
                        res = g_model.generate_content(prompt)
                        if hasattr(res, "text") and res.text:
                            return res.text.strip()
                        elif hasattr(res, "parts") and res.parts:
                            return res.parts[0].text.strip()
                    except Exception:
                        continue

            return f"⚠️ Error in Explanation: Please configure GEMINI_API_KEY or install transformers & torch to generate explanations for '{topic}'."
    except Exception as e:
        return f"⚠️ Error in Explanation: {e}"
