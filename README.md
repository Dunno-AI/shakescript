
# 🎭 ShakeScript - An AI-Based Story Creation Platform

ShakeScript is a cutting-edge, AI-powered storytelling system designed to generate immersive, multi-episode narratives with rich characters, evolving plots, and long-term memory. By blending the strengths of **GPT-4o** and **Google Gemini**, it overcomes traditional limitations in AI storytelling, such as token constraints and narrative inconsistencies.

---

## 🔍 The Problem

Traditional AI-generated stories often struggle with:

| Challenge | Description |
|---|---|
| 🔄 **Narrative Coherence** | Maintaining seamless connections between episodes. |
| 🧠 **Token Limitations** | Handling the restricted context windows of large language models. |
| 👤 **Character Consistency** | Preserving character traits, relationships, and emotional states. |
| 📚 **Extended Narratives** | Structuring long stories into coherent, episodic chunks. |
| 💾 **AI Memory** | Retaining relevant story context across multiple episodes. |

---

## 🚀 ShakeScript: Your AI Storytelling Engine

**ShakeScript** enables long-form storytelling with AI memory, human feedback integration, and cultural nuance.

### ✅ Core Capabilities

-   Accepts brief prompts, including genres, tropes, or plotlines.
-   Generates multi-episode stories with detailed world-building and character arcs.
-   Maintains narrative continuity using metadata and embeddings.
-   Supports **Hinglish** storytelling.
-   Offers both AI-driven and human-in-the-loop episode refinement.
-   Utilizes a robust database and semantic embeddings for memory.

---

## 📂 Architecture & Workflow

### 1️⃣ Prompt-to-Metadata Extraction (via Google Gemini)

-   **Endpoint**: `/stories`
-   Gemini extracts:
    -   **Characters**: Names, roles, relationships, and emotions.
    -   **Settings**: Detailed location descriptions.
    -   **Structure**: Exposition → Climax → Denouement.
    -   **Theme & Tone**: (e.g., Suspenseful, Romantic).
-   Data is stored in Supabase in the `stories` and `characters` tables.

---

### 2️⃣ Episode Generation (via GPT-4o)

#### Initial Episode

-   Uses structured metadata to generate an episode that aligns with the story's outline (e.g., Exposition).

#### Subsequent Episodes

-   Retrieves up to three past episodes for context.
-   Embeddings fetch relevant content chunks to ensure long-form continuity.
-   Ensures character consistency, thematic alignment, and narrative progression.

#### Storage

-   Saves episode content, titles, summaries, and emotional states in the `episodes` table.
-   Splits episodes into semantic chunks using `SemanticSplitterNodeParser`.
-   Vectorizes and stores these chunks in the `chunks` table.

---

### 3️⃣ Validation & Refinement (via Gemini)

#### AI Validation (`validation.py`)

-   Checks for timeline alignment, character consistency (location and motivation), and coherence in dialogue and tone.
-   Refines the story up to three times if inconsistencies are found.

#### Human Feedback (`episodes.py`)

-   Users can refine episodes via the `/refine-batch` endpoint.
-   Gemini regenerates content while preserving the story's core elements.

#### Batch Processing (`refinement.py`)

-   The default batch size is two episodes.
-   The intermediate state is stored in `current_episodes_content`.

---

### 4️⃣ Memory Management

#### Supabase (`db_service.py`)

-   Tracks the `current_episode`, `key_events`, `timeline`, and character evolution.

#### Embedding Service (`embedding_service.py`)

-   Uses Hugging Face embeddings to vectorize story chunks.
-   Scores relevance based on the characters involved and episode order, enabling memory-aware story generation.

---

### 5️⃣ API & Frontend Integration

#### FastAPI Backend

-   **Endpoints**:
    -   `/stories` – Create a new story.
    -   `/generate-batch` – Generate a batch of episodes.
    -   `/validate-batch` – Perform AI validation.
    -   `/refine-batch` – Handle human feedback and refinement.
-   Uses Pydantic models for structured data (`schemas.py`).

#### Frontend

-   A **React/Next.js** user interface.
-   **Features**:
    -   Episode display.
    -   Character profiles.
    -   Hinglish support.
    -   Real-time story updates.

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **AI & NLP** | GPT-4o, Google Gemini, Hugging Face Embeddings |
| **Backend** | FastAPI, Pydantic, Asyncio |
| **Database** | Supabase (PostgreSQL) |
| **Embeddings & Retrieval**| LlamaIndex (`SemanticSplitterNodeParser`), Supabase Vector DB |
| **Language** | Python 3.13 with type hints |

---

## 🎯 Key Achievements

-   🏆 **Multi-Episode Consistency** – Maintains coherent and evolving narratives.
-   💡 **Token Limit Workaround** – Smart retrieval with embeddings.
-   👤 **Character Evolution** – Tracks character traits, arcs, and relationships.
-   🔁 **AI + Human Refinement** – Combines LLM polish with user feedback.
-   🌍 **Hinglish Support** – Culturally tuned storytelling.

---

## 🖼️ Visuals & Evaluations

### 🧩 Model Pipeline

<p align="center"> <img src="https://raw.githubusercontent.com/RaviThakur1002/shakescript/main/charts_and_pipeline/pipeline.png" alt="Model Pipeline" width="700"/> </p>

---

### 📈 Radar Chart - Story Attribute Comparison

<p align="center"> <img src="https://raw.githubusercontent.com/RaviThakur1002/shakescript/main/charts_and_pipeline/radarChart.png" alt="Radar Chart" width="500"/> </p>

---

### 🪱 Worm Graph - Evaluation Metrics (out of 10)

<p align="center"> <img src="https://raw.githubusercontent.com/RaviThakur1002/shakescript/main/charts_and_pipeline/wormChart.png" alt="Worm Chart" width="700"/> </p>

---

## 🔮 Future Enhancements

| Feature | Description |
|---|---|
| 🎮 **Interactive Storylines**| Allow users to influence the story's direction. |
| 🎧 **TTS Narration** | Add audio playback with Text-to-Speech. |
| 🧠 **Custom AI Models** | Fine-tune LLMs for specific genres or styles. |
| 📱 **Frontend UI** | A responsive, real-time React/Next.js interface. |
| 🔍 **Smart Retrieval** | Advanced hybrid/cosine similarity for chunk searching. |

---

## 💬 Final Thoughts

ShakeScript redefines AI-powered storytelling by:

-   Solving token limitation challenges.
-   Supporting long-form, culturally nuanced narratives.
-   Seamlessly blending LLMs, embeddings, and human input.

> 🎉 Let the stories unfold — with ShakeScript, your narrative has no limits.
