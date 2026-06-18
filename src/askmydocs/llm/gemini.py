from askmydocs.config import GEMINI_MODEL, GEMINI_API_KEY
from askmydocs.types import SearchResult, RagResponse
from askmydocs.llm.prompt import get_system_prompt, build_context

_client = None


def _get_client():
    global _client
    if _client is None:
        from google import genai
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def generate_answer(question: str, results: list[SearchResult], lang: str = "fr") -> RagResponse:
    from google.genai import types
    context = build_context(results)
    ctx_label = "Contexte" if lang == "fr" else "Context"
    response = _get_client().models.generate_content(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(system_instruction=get_system_prompt(lang)),
        contents=f"{ctx_label} :\n{context}\n\nQuestion : {question}",
    )
    return {"answer": response.text, "sources": results}
