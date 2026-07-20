"""Interface Streamlit pour AskMyDocs."""
import streamlit as st

from askmydocs.config import UPLOADS_DIR
from askmydocs.llm.factory import PROVIDER_REGISTRY
from askmydocs.rag import ingest, ask

# Nom affiche pour chaque provider (les noms de produit ne se traduisent pas)
PROVIDER_DISPLAY_NAMES = {
    "ollama": "Ollama",
    "gemini": "Gemini",
    "claude": "Claude",
    "openai": "OpenAI",
    "deepseek": "DeepSeek",
}


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
        "provider_label": "Provider LLM",
        "model_label": "Modèle",
        "local_ok": "✅ 100% local : aucune donnée ne quitte la machine.",
        "cloud_warning": "⚠️ Les données sont envoyées à un service cloud. Non conforme RGPD pour des documents sensibles.",
        "unavailable_caption": "Providers indisponibles : {details}",
        "missing_env_var": "{name} (variable {env_var} manquante)",
        "service_unreachable": "{name} (service injoignable)",
        "no_provider_available": "⚠️ Aucun provider LLM disponible. Configure au moins une clé API dans ton fichier .env, ou démarre le service Ollama.",
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
        "provider_label": "LLM provider",
        "model_label": "Model",
        "local_ok": "✅ 100% local: no data leaves your machine.",
        "cloud_warning": "⚠️ Data is sent to a cloud service. Not GDPR-compliant for sensitive documents.",
        "unavailable_caption": "Unavailable providers: {details}",
        "missing_env_var": "{name} ({env_var} missing)",
        "service_unreachable": "{name} (service unreachable)",
        "no_provider_available": "⚠️ No LLM provider available. Set at least one API key in your .env file, or start the Ollama service.",
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
    if "model" not in st.session_state:
        st.session_state.model = PROVIDER_REGISTRY["ollama"].DEFAULT_MODEL
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

    # Un provider est disponible si sa clé API est présente (cloud) ou si le
    # service est joignable (Ollama, local). Les providers indisponibles sont
    # masqués du sélecteur, avec le détail de ce qui manque juste en dessous.
    available_providers = []
    unavailable_providers = []
    for name, provider_cls in PROVIDER_REGISTRY.items():
        if provider_cls().is_available():
            available_providers.append(name)
        else:
            unavailable_providers.append(name)

    if not available_providers:
        st.error(t["no_provider_available"])
    else:
        if st.session_state.provider not in available_providers:
            st.session_state.provider = available_providers[0]
            st.session_state.model = PROVIDER_REGISTRY[st.session_state.provider].DEFAULT_MODEL

        provider = st.radio(
            t["provider_label"],
            options=available_providers,
            format_func=lambda x: PROVIDER_DISPLAY_NAMES[x],
            index=available_providers.index(st.session_state.provider),
        )
        if provider != st.session_state.provider:
            st.session_state.provider = provider
            st.session_state.model = PROVIDER_REGISTRY[provider].DEFAULT_MODEL

        supported_models = PROVIDER_REGISTRY[provider].SUPPORTED_MODELS
        model = st.selectbox(
            t["model_label"],
            options=supported_models,
            index=supported_models.index(st.session_state.model)
            if st.session_state.model in supported_models
            else 0,
        )
        st.session_state.model = model

        if PROVIDER_REGISTRY[provider].IS_LOCAL:
            st.caption(t["local_ok"])
        else:
            st.caption(t["cloud_warning"])

    if unavailable_providers:
        def _reason(name: str) -> str:
            env_var = getattr(PROVIDER_REGISTRY[name], "ENV_VAR", None)
            if env_var:
                return t["missing_env_var"].format(
                    name=PROVIDER_DISPLAY_NAMES[name], env_var=env_var
                )
            return t["service_unreachable"].format(name=PROVIDER_DISPLAY_NAMES[name])

        details = ", ".join(_reason(name) for name in unavailable_providers)
        st.caption(t["unavailable_caption"].format(details=details))


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
                response = ask(
                    question,
                    provider=st.session_state.provider,
                    model=st.session_state.model,
                    lang=st.session_state.lang,
                )
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
