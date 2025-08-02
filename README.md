# 🎭 ShakeScript - An AI-Based Story Creation Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Framework-FastAPI-green.svg" alt="Framework">
  <img src="https://img.shields.io/badge/Frontend-React-blue.svg" alt="Frontend">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <a href="https://github.com/RaviThakur1002/shakescript/stargazers"><img src="https://img.shields.io/github/stars/RaviThakur1002/shakescript" alt="Stars Badge"/></a>
</p>

<p align="center"> <img src="https://raw.githubusercontent.com/RaviThakur1002/shakescript/main/charts_and_pipeline/Intro.png" alt="ShakeScript Introduction" width="700"/> </p>

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
-   Utilizes a robust database and Gemini-based semantic embeddings for memory.

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
-   Gemini-generated embeddings fetch relevant story chunks to ensure long-form continuity.
-   Ensures character consistency, thematic alignment, and narrative progression.

#### Storage

-   Saves episode content, titles, summaries, and emotional states in the `episodes` table.
-   Splits episodes into semantic chunks using `SemanticSplitterNodeParser`.
-   Vectorizes and stores these chunks in the `chunks` table using Gemini Embeddings.

---

### 3️⃣ Memory Management

#### Supabase (`db_service.py`)

-   Tracks the `current_episode`, `key_events`, `timeline`, and character evolution.

#### Embedding Service (`embedding_service.py`)

-   Uses **Google Gemini Embeddings** (`models/embedding-001`) to vectorize story chunks.
-   Scores relevance based on the characters involved and episode order, enabling memory-aware story generation.

---

### 4️⃣ API & Frontend Integration

#### FastAPI Backend

-   **Endpoints**:
    -   `/stories` – Create a new story.
    -   `/generate-batch` – Generate a batch of episodes.
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

<p align="center">
  <strong>AI & NLP</strong><br>
  <img src="https://img.shields.io/badge/GPT--4o-000000?style=for-the-badge&logo=openai&logoColor=white" alt="GPT-4o">
  <img src="https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini">
  <img src="https://img.shields.io/badge/Gemini%20Embedding-34A853?style=for-the-badge&logo=google&logoColor=white" alt="Gemini Embedding">
</p>
<p align="center">
  <strong>Backend</strong><br>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic">
  <img src="https://img.shields.io/badge/Asyncio-8A2BE2?style=for-the-badge&logo=python&logoColor=white" alt="Asyncio">
</p>
<p align="center">
  <strong>Database & Embeddings</strong><br>
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/LlamaIndex-6B45BC?style=for-the-badge" alt="LlamaIndex">
</p>

---

## 🎯 Key Achievements

-   🏆 **Multi-Episode Consistency** – Maintains coherent and evolving narratives.
-   💡 **Token Limit Workaround** – Smart retrieval using **Gemini Embeddings**.
-   👤 **Character Evolution** – Tracks character traits, arcs, and relationships.
-   🔁 **Human Refinement** – Combines LLM polish with user feedback.
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
| 🎧 **TTS Narration** | Add audio playback with Text-to-Speech. |
| 🧠 **Custom AI Models** | Fine-tune LLMs for specific genres or styles. |


---

## 💬 Final Thoughts

ShakeScript redefines AI-powered storytelling by:

-   Solving token limitation challenges.
-   Supporting long-form, culturally nuanced narratives.
-   Seamlessly blending LLMs, embeddings, and human input.

> 🎉 Let the stories unfold — with ShakeScript, your narrative has no limits.

---

<p align="center">
  Made with ❤️ by the ShakeScript AI Team
</p>
