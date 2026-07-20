# 📚 AskMyDocs

> Le Retrieval-Augmented Generation est la colonne vertébrale des systèmes de « chat avec vos documents ». Ce projet en implémente un de bout en bout, **tourne entièrement en local pour la confidentialité**, et **mesure s'il fonctionne réellement**.

Un assistant conversationnel qui répond à des questions sur vos documents (PDF, Word) grâce à une chaîne **RAG** complète, avec citation des sources et **évaluation quantitative** de la qualité des réponses.

Sa caractéristique centrale est un design **à double provider LLM** : par défaut, tout tourne **100% en local** (embeddings, recherche vectorielle *et* génération), donc aucune donnée ne quitte votre machine. C'est une approche *privacy by design*, adaptée aux documents sensibles au RGPD ; un provider cloud (Google Gemini) peut être activé en un clic lorsque la performance brute prime sur la localité des données.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-local-000000?style=for-the-badge&logo=ollama&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-vector_store-FF6B6B?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![RGPD](https://img.shields.io/badge/RGPD-compliant-2E7D32?style=for-the-badge&logo=shield&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

<p align="center">
  <img src="docs/Screen_askmydocs.png" alt="Interface AskMyDocs" width="800">
</p>

## 🎥 Démonstration

<p align="center">
  <img src="docs/gif_1_Streamlit_run.gif" alt="Lancer Streamlit" width="800">
</p>

<p align="center">
  <img src="docs/gif_2_load.gif" alt="Charger un document" width="800">
</p>

<p align="center">
  <img src="docs/gif_3_result.gif" alt="Fonctionnement" width="800">
</p>

## 🎯 Vue d'ensemble

AskMyDocs permet d'interroger un document en langage naturel. Vous posez une question, il récupère les passages pertinents du document et génère une réponse sourcée, sans halluciner, en s'appuyant uniquement sur le contenu fourni.

Le projet implémente la chaîne RAG (*Retrieval-Augmented Generation*) complète, de l'ingestion du document à la génération de la réponse, **auquel s'ajoute** un harnais d'évaluation pour mesurer objectivement ses performances.

### 🔀 Le design à double provider

La fonctionnalité phare, c'est que vous **choisissez où l'inférence a lieu**, directement depuis l'interface :

- 🔒 **Ollama (par défaut, local)** — les embeddings, la recherche vectorielle et le LLM tournent tous sur votre machine. Documents, questions et réponses ne quittent jamais l'appareil. C'est le mode conforme au RGPD, et il est par défaut pour une bonne raison : le document de test du projet est le règlement RGPD lui-même.
- ☁️ **Google Gemini (optionnel, cloud)** — un modèle plus puissant lorsque la qualité de réponse prime sur la localité des données. Un avertissement clair dans l'app rappelle que les données sont envoyées à un tiers.

Ce n'est pas un flag de config caché : l'arbitrage entre **confidentialité** et **performance** est présenté à l'utilisateur comme un choix explicite et conscient — le *privacy by design* en pratique.

Sur le plan architectural, les deux providers reposent sur une **interface unique**. Basculer de l'un à l'autre ne touche **qu'un seul package** (`src/askmydocs/llm/`) ; le reste du pipeline ignore totalement quel backend a répondu. Ce couplage faible est la décision de conception dont je suis le plus fier dans ce projet.

## ✨ Fonctionnalités

- 📄 Ingestion de documents **PDF** et **Word** (.docx)
- ✂️ Découpage (chunking) intelligent avec préservation des métadonnées (source, page)
- 🔍 Recherche sémantique via des embeddings multilingues (optimisés pour le français)
- 🔀 **Double provider LLM** avec bascule en un clic : Ollama (local, RGPD) ou Gemini (cloud, performance)
- 🔒 **Génération 100% locale** par défaut — aucune donnée ne quitte la machine
- 🔌 **Providers interchangeables** : chaque backend expose la même fonction `generate_answer`, et un petit registre dans `llm/__init__.py` sert de point d'entrée unique, utilisé à la fois par l'UI et par le harnais d'évaluation
- 🤖 Réponses strictement ancrées dans le contexte récupéré (pas d'hallucination)
- 📌 **Citation des sources** (document + page) pour chaque réponse
- 💬 Interface de chat avec historique (Streamlit)
- 📊 **Harnais d'évaluation** : dataset annoté, métriques de récupération et de génération

## 💬 Exemple

**Q :** « Quel est le délai pour notifier une violation de données personnelles ? »

**R :** Selon l'article 33 du RGPD, une violation de données à caractère personnel doit être notifiée à l'autorité de contrôle dans les meilleurs délais et, si possible, au plus tard **72 heures** après en avoir pris connaissance [page 17].

> 📄 Sources : RGPD.pdf, p.17

## 🏗️ Architecture

```
PDF / DOCX
    │
    ▼
  Loader  ──────►  Splitter  ──────►  Embedder  ──────►  ChromaDB
(extraction)     (chunking)      (vectorisation)   (stockage vectoriel)
                                                            │
                                                            ▼
                              Question ──► Recherche sémantique (top-K)
                                                            │
                                                            ▼
                              Génération via l'interface provider
                                       ┌──────────┴──────────┐
                                       ▼                     ▼
                               Ollama (local, RGPD)   Gemini (cloud)
                                       └──────────┬──────────┘
                                                  ▼
                                      Réponse + sources citées
```

Le pipeline est exposé via deux fonctions de haut niveau dans `rag.py` :
- `ingest(file_path)` : charge, découpe et indexe un document
- `ask(question, provider=...)` : récupère les passages pertinents et génère la réponse avec le provider choisi

Chaque provider est un petit module (`llm/ollama.py`, `llm/gemini.py`) exposant la **même fonction** : `generate_answer(question, results, lang=...) -> RagResponse`. Un registre léger dans `llm/__init__.py` associe un nom de provider à son module et expose un unique point d'entrée, `generate_answer(question, results, provider=None)`, utilisé à la fois par l'UI Streamlit et par le harnais d'évaluation. Ajouter un provider revient à écrire un module et à ajouter une ligne à ce registre — rien dans le pipeline, l'UI ou le harnais d'éval n'a besoin de changer.

## 🛠️ Stack technique

| Couche | Outil | Pourquoi ce choix |
|---|---|---|
| Langage | Python 3.11+ | Standard pour le ML/data |
| Gestion des dépendances | uv | Rapide, moderne, locks reproductibles |
| Extraction PDF / DOCX | pypdf, python-docx | Léger, sans dépendances système |
| Chunking | langchain-text-splitters | Découpage récursif robuste |
| Embeddings | sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`) | Local, gratuit, multilingue (français) |
| Vector store | ChromaDB | Persistance locale sans configuration |
| LLM (par défaut) | Ollama, local | 100% on-device, aucune donnée ne quitte la machine (RGPD) |
| LLM (cloud optionnel) | Google Gemini | Alternative cloud quand la performance prime sur la localité |
| UI | Streamlit | Interface Python-native rapide |
| Évaluation | dataset annoté + métriques maison | Contrôle total sur ce qui est mesuré |
| Tests | pytest | Couverture de la logique d'ingestion et de récupération |

> 💡 Le modèle local se configure en une ligne (`OLLAMA_MODEL` dans `config.py`). `llama3.2` est le modèle par défaut ; passer à `mistral` améliore la sortie en français au prix de plus de RAM — exactement le type de bascule que le couplage faible rend trivial.

## ⚙️ Prérequis

- **Python 3.11+** et [uv](https://docs.astral.sh/uv/)
- **~6 Go de RAM** pour faire tourner confortablement un modèle 7B local (ex. `mistral`) en parallèle du modèle d'embeddings. Des modèles plus légers comme `llama3.2` (3B) fonctionnent avec moins. Sous WSL, allouez explicitement la mémoire dans `.wslconfig` pour éviter les kills par manque de mémoire (OOM).
- *(Optionnel)* une clé API Google AI Studio, uniquement si vous souhaitez utiliser le provider Gemini.

## 🤖 Providers LLM supportés

| Provider | Type | Modèles | Variable d'environnement |
|---|---|---|---|
| Ollama | Local | `llama3.2` (défaut), `mistral` | `OLLAMA_HOST` (optionnel, défaut `http://localhost:11434`) |
| Google Gemini | Cloud | `gemini-2.5-flash` | `GEMINI_API_KEY` |

Le provider par défaut est défini par `LLM_PROVIDER` dans `.env` (`ollama` par défaut). Si `GEMINI_API_KEY` est absente, Gemini est simplement masqué dans l'UI (avec une légende indiquant la variable manquante) et l'app se rabat sur le backend local — elle ne plante jamais au démarrage.

## 🚀 Installation

```bash
# Cloner le dépôt
git clone https://github.com/liliandoublet/askmydocs.git
cd askmydocs

# Installer les dépendances avec uv
uv sync
```

### Par défaut : LLM local avec Ollama (recommandé)

```bash
# Installer Ollama (macOS / Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Télécharger un modèle
ollama pull llama3.2

# S'assurer que le serveur Ollama tourne (il écoute sur localhost:11434)
ollama serve
```

Aucune clé API requise, tout tourne en local.

### Optionnel : LLM cloud avec Gemini

```bash
cp .env.example .env
# Éditer .env et ajouter votre GEMINI_API_KEY
```

Obtenez une clé API sur [Google AI Studio](https://aistudio.google.com/apikey). Elle n'est nécessaire que si vous comptez utiliser le provider Gemini.

## 💻 Utilisation

### Lancer l'application

```bash
uv run streamlit run app.py
```

Chargez un document dans la barre latérale, indexez-le, choisissez votre provider (Ollama ou Gemini) dans la barre latérale, puis posez vos questions.

### Ligne de commande

```bash
# Exécuter le pipeline complet sur un document
uv run python -m askmydocs.rag data/uploads/mon_document.pdf "Ma question ?"
```

## 📊 Évaluation

Le projet inclut un harnais d'évaluation qui mesure les performances du pipeline sur un dataset de questions annotées (avec pages de référence et mots-clés attendus).

```bash
uv run python -m askmydocs.eval.runner data/uploads/RGPD.pdf
```

Le chemin du document est optionnel (il vaut `data/uploads/RGPD.pdf` par défaut), et le provider est déterminé par `LLM_PROVIDER` dans `.env` (`ollama` par défaut). Le harnais lit le dataset annoté depuis `data/eval/qa_dataset.json` et écrit les résultats détaillés dans `data/eval/results.json`.

### Métriques mesurées

Le harnais **découple récupération et génération**, pour diagnostiquer précisément l'origine d'un échec : un hit rate faible pointe vers un problème de récupération, tandis qu'un bon hit rate accompagné de refus pointe vers un problème de prompt ou de génération.

| Métrique | Ce qu'elle mesure |
|---|---|
| **Hit rate** | La récupération trouve-t-elle au moins une page pertinente ? |
| **Précision** | Quelle proportion des chunks récupérés est pertinente ? |
| **Keyword recall** | La réponse générée contient-elle les faits attendus ? |
| **Taux de refus** | À quelle fréquence le LLM répond « je ne trouve pas » |

### Résultats sur le document RGPD (88 pages, 626 chunks)

Comme les deux providers partagent exactement le même pipeline de récupération, les métriques de récupération (hit rate, précision) sont identiques entre eux — seules les métriques de génération (keyword recall, taux de refus) reflètent le modèle. Le tableau reporte les deux pour que la comparaison reste honnête.

| Métrique | Ollama (`llama3.2`, local) | Gemini (cloud) |
|---|---|---|
| Hit rate | 50,0 % | _À venir_ |
| Précision | 11,7 % | _À venir_ |
| Keyword recall | 58,3 % | _À venir_ |
| Taux de refus | 2/10 | _À venir_ |

> **Lecture des chiffres :** une précision faible est attendue sur ce corpus.
> Avec seulement 1 à 2 pages pertinentes sur 88, même une récupération parfaite
> ne peut pas obtenir un score élevé. Les signaux significatifs ici sont le
> **hit rate** (la bonne page est-elle trouvée ?) et le **keyword recall**
> (la réponse est-elle factuellement correcte ?).

> **L'arbitrage du local, mesuré honnêtement :** tout faire tourner on-device
> n'est pas gratuit. Un petit modèle local est plus lent (des dizaines de secondes
> par réponse sur CPU) et produit un français plus brut qu'un modèle cloud de
> pointe. Le design à double provider existe précisément pour faire de cet
> arbitrage un choix délibéré plutôt qu'un coût caché — confidentialité par
> défaut, performance à la demande.

## 🧠 Notes d'ingénierie

Quelques vrais problèmes résolus en construisant ce projet, et ce qu'ils m'ont appris :

- **Décalage modèle d'embeddings / langue** : le modèle initial, centré sur
  l'anglais, séparait mal le texte français (un écart discriminant de seulement
  ~0,08 entre paires de phrases liées et non liées). Diagnostiquer ce point et
  passer à un modèle multilingue a plus que doublé cet écart. Leçon : adaptez le
  modèle d'embeddings à la langue de votre corpus, et *mesurez-le* plutôt que de
  le supposer.
- **Bruit d'extraction polluant l'index** : les pages riches en figures
  produisaient des chunks d'un caractère (simples numéros de page) qui polluaient
  l'index vectoriel et remontaient comme résultats non pertinents. Ajout d'un
  filtre de longueur minimale (`MIN_CHUNK_SIZE`), couvert par un test unitaire.
  Leçon : en RAG, la qualité de l'ingestion compte autant que le modèle.
  *Garbage in, garbage out.*
- **Limites de débit des API externes** : envoyer tout le batch d'évaluation à
  l'API Gemini d'affilée déclenchait des réponses de rate-limit (429). Le runner
  d'éval espace les requêtes avec un délai fixe pour rester sous le quota. La
  leçon plus profonde a orienté tout le design : le backend Ollama local supprime
  entièrement la dépendance externe — et ses limites de débit — ce qui explique en
  grande partie pourquoi le local est le mode par défaut.
- **Un couplage faible qui a payé** : le projet ne tournait au départ que sur
  Gemini. Ajouter un provider entièrement local a consisté à écrire un module
  (`llm/ollama.py`) exposant la même fonction `generate_answer` et à ajouter une
  seule ligne au registre de providers — `rag.py`, l'UI et le harnais d'éval n'ont
  jamais été touchés. Quand une décision d'architecture permet de remplacer un
  composant central en ajoutant un seul fichier, c'est que les coutures sont au
  bon endroit.
- **Les contraintes opérationnelles sont réelles** : faire tourner un modèle 7B
  en local a exposé des limites de RAM strictes (kills OOM sous l'allocation
  mémoire par défaut de WSL). Diagnostiquer avec `free -h` et augmenter le budget
  mémoire/swap de WSL a réglé le problème. L'inférence locale n'est pas qu'une
  décision de code — c'est aussi une décision de gestion des ressources.

## 🔬 Visualisation des embeddings

Le notebook `notebooks/01_exploration.ipynb` projette l'espace d'embeddings du corpus en 2D (PCA). Il montre le regroupement thématique des chunks et la position d'une requête parmi les passages pertinents.

## 📁 Structure du projet

```
askmydocs/
├── src/askmydocs/
│   ├── config.py          # Configuration centralisée
│   ├── types.py           # Types partagés (TypedDict) : SearchResult, RagResponse
│   ├── loader.py          # Extraction PDF / DOCX
│   ├── splitter.py        # Chunking
│   ├── embedder.py        # Génération des embeddings
│   ├── vectorstore.py     # Stockage et recherche (ChromaDB)
│   ├── rag.py             # Orchestration du pipeline : ingest() + ask()
│   ├── llm/               # Génération des réponses
│   │   ├── __init__.py    # Registre de providers + point d'entrée generate_answer()
│   │   ├── ollama.py      # LLM local (par défaut, confidentialité)
│   │   ├── gemini.py      # LLM cloud (Google)
│   │   └── prompt.py      # Prompt partagé pour la génération
│   └── eval/              # Harnais d'évaluation
│       ├── metrics.py
│       └── runner.py
├── notebooks/             # Exploration et visualisation
├── tests/                 # Tests unitaires (pytest)
├── data/                  # Documents et dataset d'évaluation
└── app.py                 # Interface Streamlit
```

## 🧪 Tests

```bash
uv run pytest -v
```

La suite couvre la logique d'ingestion et de récupération — le loader, le splitter et le pipeline RAG (`tests/test_loader.py`, `tests/test_splitter.py`, `tests/test_rag.py`). Elle s'exécute sans accès réseau ni clé API configurée.

## 🔭 Améliorations possibles

- Benchmarker Gemini contre Ollama sur l'ensemble du set d'évaluation (compléter le tableau ci-dessus)
- Tester `mistral` comme modèle local pour une meilleure sortie en français
- Re-ranking des résultats avec un cross-encoder
- Recherche hybride (sémantique + mots-clés / BM25)
- Étendre le dataset d'évaluation
- Support de l'OCR pour les PDF scannés

## 📄 Licence

Ce projet est sous licence MIT, voir le fichier [LICENSE](LICENSE) pour plus de détails.
