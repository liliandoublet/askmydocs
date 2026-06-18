import ollama

from askmydocs.config import OLLAMA_MODEL, OLLAMA_HOST
from askmydocs.types import SearchResult, RagResponse
from askmydocs.llm.prompt import get_system_prompt, build_context

_client = ollama.Client(host=OLLAMA_HOST)


def generate_answer(question: str, results: list[SearchResult], lang: str = "fr") -> RagResponse:
    context = build_context(results)
    ctx_label = "Contexte" if lang == "fr" else "Context"
    response = _client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": get_system_prompt(lang)},
            {"role": "user", "content": f"{ctx_label} :\n{context}\n\nQuestion : {question}"},
        ],
    )
    return {"answer": response.message.content, "sources": results}
