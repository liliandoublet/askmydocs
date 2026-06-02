"""Interface Streamlit pour AskMyDocs."""
import tempfile
from pathlib import Path

import streamlit as st

from askmydocs.config import UPLOADS_DIR, check_config
from askmydocs.rag import ingest, ask


# --- Configuration de la page ---
st.set_page_config(page_title="AskMyDocs", page_icon="📚", layout="wide")


# --- Initialisation du session_state ---
def init_state() -> None:
    """Initialise les variables de session si elles n'existent pas."""
    if "messages" not in st.session_state:
        st.session_state.messages = []        # historique [(role, contenu, sources)]
    if "indexed_file" not in st.session_state:
        st.session_state.indexed_file = None   # nom du fichier indexé


init_state()


# --- Sidebar : upload et indexation ---
with st.sidebar:
    st.title("📚 AskMyDocs")
    st.caption("Pose des questions à tes documents")

    uploaded_file = st.file_uploader(
        "Charge un document",
        type=["pdf", "docx"],
        help="Formats acceptés : PDF, Word (.docx)",
    )

    if uploaded_file is not None:
        if st.button("📥 Indexer le document", use_container_width=True):
            with st.spinner("Indexation en cours... (ça peut prendre 1-2 min)"):
                # Sauvegarde temporaire du fichier uploadé sur le disque
                UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
                file_path = UPLOADS_DIR / uploaded_file.name
                file_path.write_bytes(uploaded_file.getbuffer())

                # Ingestion (avec reset pour repartir propre)
                n_chunks = ingest(file_path, reset=True)

                st.session_state.indexed_file = uploaded_file.name
                st.session_state.messages = []   # on vide le chat pour le nouveau doc

            st.success(f"✅ {uploaded_file.name} indexé ({n_chunks} chunks)")

    # Statut courant
    if st.session_state.indexed_file:
        st.info(f"📄 Document actif : **{st.session_state.indexed_file}**")
    else:
        st.warning("Aucun document indexé pour l'instant.")


# --- Zone principale : le chat ---
st.header("💬 Conversation")

if not st.session_state.indexed_file:
    st.info("👈 Commence par charger et indexer un document dans la barre latérale.")
else:
    # Affichage de l'historique
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Affiche les sources sous les réponses de l'assistant
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("📚 Sources"):
                    for s in msg["sources"]:
                        st.caption(
                            f"• **{s['source']}** — page {s['page']} "
                            f"(pertinence : {s['score']})"
                        )

    # Champ de saisie
    if question := st.chat_input("Pose ta question..."):
        # 1. Affiche la question de l'utilisateur
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # 2. Génère et affiche la réponse
        with st.chat_message("assistant"):
            with st.spinner("Réflexion..."):
                response = ask(question)
            st.markdown(response["answer"])

            if response["sources"]:
                with st.expander("📚 Sources"):
                    for s in response["sources"]:
                        st.caption(
                            f"• **{s['source']}** — page {s['page']} "
                            f"(pertinence : {s['score']})"
                        )

        # 3. Sauvegarde la réponse dans l'historique
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["answer"],
            "sources": response["sources"],
        })