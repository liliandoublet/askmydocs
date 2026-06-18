"""Interface Streamlit pour AskMyDocs."""
import streamlit as st

from askmydocs.config import UPLOADS_DIR, GEMINI_API_KEY
from askmydocs.rag import ingest, ask


# --- Translations ---
TRANSLATIONS = {
    "fr": {
        "page_title": "AskMyDocs",
        "sidebar_caption": "Pose des questions à tes documents",
        "upload_label": "Charge un document",
        "upload_help": "Formats acceptés : PDF, Word (.docx)",
        "index_button": "📥 Indexer le document",
        "indexing_spinner": "Indexation en cours... (ça peut prendre 1-2 min)",
        "index_success": "✅ {name} indexé ({n} chunks)",
        "active_doc": "📄 Document actif : **{name}**",
        "no_doc": "Aucun document indexé pour l'instant.",
        "llm_label": " Modèle LLM",
        "ollama_label": "🔒 Ollama (local, RGPD)",
        "gemini_label": "☁️ Gemini (cloud)",
        "gemini_missing_key": "⚠️ GEMINI_API_KEY manquante — Gemini indisponible.",
        "gemini_warning": "⚠️ Les données sont envoyées à Google. Non conforme RGPD pour des documents sensibles.",
        "ollama_ok": "✅ 100% local — aucune donnée ne quitte la machine.",
        "chat_header": "💬 Conversation",
        "no_doc_info": "👈 Commence par charger et indexer un document dans la barre latérale.",
        "sources_label": "📚 Sources",
        "source_line": "• **{source}** — page {page} (pertinence : {score})",
        "chat_input": "Pose ta question...",
        "thinking_spinner": "Réflexion...",
        "language_label": "🌐 Langue / Language",
    },
    "en": {
        "page_title": "AskMyDocs",
        "sidebar_caption": "Ask questions about your documents",
        "upload_label": "Upload a document",
        "upload_help": "Accepted formats: PDF, Word (.docx)",
        "index_button": "📥 Index document",
        "indexing_spinner": "Indexing… (this may take 1-2 min)",
        "index_success": "✅ {name} indexed ({n} chunks)",
        "active_doc": "📄 Active document: **{name}**",
        "no_doc": "No document indexed yet.",
        "llm_label": " LLM Model",
        "ollama_label": "🔒 Ollama (local, GDPR)",
        "gemini_label": "☁️ Gemini (cloud)",
        "gemini_missing_key": "⚠️ GEMINI_API_KEY missing — Gemini unavailable.",
        "gemini_warning": "⚠️ Data is sent to Google. Not GDPR-compliant for sensitive documents.",
        "ollama_ok": "✅ 100% local — no data leaves your machine.",
        "chat_header": "💬 Conversation",
        "no_doc_info": "👈 Start by uploading and indexing a document in the sidebar.",
        "sources_label": "📚 Sources",
        "source_line": "• **{source}** — page {page} (relevance: {score})",
        "chat_input": "Ask your question…",
        "thinking_spinner": "Thinking…",
        "language_label": "🌐 Langue / Language",
    },
}

# --- Page config ---
st.set_page_config(page_title="AskMyDocs", page_icon="📚", layout="wide")


# --- Session state init ---
def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "indexed_file" not in st.session_state:
        st.session_state.indexed_file = None
    if "provider" not in st.session_state:
        st.session_state.provider = "ollama"
    if "lang" not in st.session_state:
        st.session_state.lang = "fr"


init_state()
t = TRANSLATIONS[st.session_state.lang]


# --- Sidebar ---
with st.sidebar:
    st.title("📚 AskMyDocs")
    st.caption(t["sidebar_caption"])

    # Language selector
    lang_choice = st.radio(
        t["language_label"],
        options=["fr", "en"],
        format_func=lambda x: "🇫🇷 Français" if x == "fr" else "🇬🇧 English",
        index=0 if st.session_state.lang == "fr" else 1,
        horizontal=True,
    )
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

    st.divider()

    uploaded_file = st.file_uploader(
        t["upload_label"],
        type=["pdf", "docx"],
        help=t["upload_help"],
    )

    if uploaded_file is not None:
        if st.button(t["index_button"], use_container_width=True):
            with st.spinner(t["indexing_spinner"]):
                UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
                file_path = UPLOADS_DIR / uploaded_file.name
                file_path.write_bytes(uploaded_file.getbuffer())
                n_chunks = ingest(file_path, reset=True)
                st.session_state.indexed_file = uploaded_file.name
                st.session_state.messages = []

            st.success(t["index_success"].format(name=uploaded_file.name, n=n_chunks))

    if st.session_state.indexed_file:
        st.info(t["active_doc"].format(name=st.session_state.indexed_file))
    else:
        st.warning(t["no_doc"])

    st.divider()
    provider = st.radio(
        t["llm_label"],
        options=["ollama", "gemini"],
        format_func=lambda x: {
            "ollama": t["ollama_label"],
            "gemini": t["gemini_label"],
        }[x],
        index=0,
    )
    st.session_state.provider = provider

    if provider == "gemini":
        if not GEMINI_API_KEY:
            st.error(t["gemini_missing_key"])
        st.caption(t["gemini_warning"])
    else:
        st.caption(t["ollama_ok"])


# --- Main chat area ---
st.header(t["chat_header"])

if not st.session_state.indexed_file:
    st.info(t["no_doc_info"])
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander(t["sources_label"]):
                    for s in msg["sources"]:
                        st.caption(t["source_line"].format(
                            source=s["source"], page=s["page"], score=s["score"]
                        ))

    if question := st.chat_input(t["chat_input"]):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner(t["thinking_spinner"]):
                response = ask(question, provider=st.session_state.provider, lang=st.session_state.lang)
            st.markdown(response["answer"])

            if response["sources"]:
                with st.expander(t["sources_label"]):
                    for s in response["sources"]:
                        st.caption(t["source_line"].format(
                            source=s["source"], page=s["page"], score=s["score"]
                        ))

        st.session_state.messages.append({
            "role": "assistant",
            "content": response["answer"],
            "sources": response["sources"],
        })
