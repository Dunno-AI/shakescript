# 🎭 ShakeScript - AI-Based Story Creation Platform

ShakeScript is a cutting-edge, AI-powered storytelling system designed to generate immersive, multi-episode narratives with rich characters, evolving plots, and long-term memory. By blending the strengths of GPT-4o and Google Gemini, it overcomes traditional limitations in AI storytelling—like token constraints and inconsistent narratives.

---

## 🔍 Problem Statement

Traditional AI-generated stories often struggle with:

| Challenge                        | Description                                                             |
|----------------------------------|-------------------------------------------------------------------------|
| 🔄 Narrative Coherence           | Maintaining seamless connections between episodes                       |
| 🧠 Token Limitations             | Handling restricted context windows in large language models            |
| 👤 Character Consistency         | Preserving character traits, relationships, and emotional states        |
| 📚 Extended Narratives           | Structuring long stories into coherent, episodic chunks                 |
| 💾 AI Memory Integration         | Retaining relevant story context across episodes                        |

---

## 🚀 ShakeScript: Your AI Storytelling Engine

**ShakeScript** enables long-form storytelling with AI memory, human feedback integration, and cultural nuance.

### ✅ Core Capabilities

- Accepts brief prompts (genre, trope, or plotline)
- Generates multi-episode stories with world-building and character arcs
- Maintains narrative continuity via metadata & embeddings
- Supports Hinglish storytelling
- Offers both AI-driven and human-in-the-loop episode refinement
- Uses a robust database + semantic embeddings for memory

---

## 📂 Architecture & Workflow

### 1️⃣ Prompt to Metadata Extraction (via Google Gemini)

- Endpoint: `/stories`
- Gemini extracts:
  - **Characters**: Names, roles, relationships, emotions
  - **Settings**: Detailed location descriptions
  - **Structure**: Exposition → Climax → Denouement
  - **Theme & Tone**: (e.g., Suspenseful, Romantic)
- Data stored in Supabase:
  - `stories`, `characters` tables

---

### 2️⃣ Episode Generation (via GPT-4o)

#### Initial Episode

- Uses structured metadata
- Generates the episode aligned to outline (e.g., Exposition)

#### Subsequent Episodes

- Retrieves up to 2-3 past episodes for context
- Embeddings fetch relevant content chunks for long-form continuity
- Ensures:
  - Character consistency
  - Thematic alignment
  - Narrative progression

#### Storage

- Saves episode content, title, summary, emotion in `episodes` table
- Splits episode into semantic chunks using `SemanticSplitterNodeParser`
- Vectorizes & stores in `chunks` table

---

### 3️⃣ Validation & Refinement (via Gemini)

#### AI Validation (`validation.py`)

- Checks:
  - Timeline alignment
  - Character location/motivation consistency
  - Dialogue and tone coherence
- Refines up to 3 times if inconsistencies found

#### Human Feedback Support (`episodes.py`)

- Users can refine via `/refine-batch`
- Gemini regenerates while preserving core elements

#### Batch Processing (`refinement.py`)

- Default batch size: 2 episodes
- Intermediate state stored in `current_episodes_content`

---

### 4️⃣ Memory Management

#### Supabase (`db_service.py`)

- Tracks:
  - `current_episode`
  - `key_events`, `timeline`
  - Character evolution

#### Embedding Service (`embedding_service.py`)

- HuggingFace embeddings vectorize story chunks
- Relevance scored based on:
  - Characters involved
  - Episode order
- Enables memory-aware story generation

---

### 5️⃣ API & Frontend Integration

#### FastAPI Backend

- Endpoints:
  - `/stories` – Create new story
  - `/generate-batch` – Batch generate episodes
  - `/validate-batch` – AI validation
  - `/refine-batch` – Human feedback and refinement
- Uses Pydantic models for structure (`schemas.py`)

#### Frontend (Planned)

- React/Next.js UI
- Features:
  - Episode display
  - Character profiles
  - Hinglish support
  - Real-time story updates

---

## 🛠️ Tech Stack

| Category              | Technologies Used                                                                 |
|-----------------------|-----------------------------------------------------------------------------------|
| AI & NLP              | GPT-4o, Google Gemini, HuggingFace Embeddings                                    |
| Backend               | FastAPI, Pydantic, Asyncio                                                       |
| Database              | Supabase (PostgreSQL)                                                            |
| Embeddings & Retrieval| LlamaIndex (`SemanticSplitterNodeParser`), Supabase Vector DB                    |
| Language              | Python 3.13 with type hints                                                      |

---

## 🎯 Key Achievements

- 🏆 **Multi-Episode Consistency** – Maintains coherent, evolving narratives
- 💡 **Token Limit Workaround** – Smart retrieval with embeddings
- 👤 **Character Evolution** – Tracks traits, arcs, and relationships
- 🔁 **AI + Human Refinement** – Combines LLM polish with user feedback
- 🌍 **Hinglish Support** – Culturally tuned storytelling

---


## 🖼️ Visuals & Evaluations

### 🧩 Model Pipeline

<p align="center"> <img src="https://raw.githubusercontent.com/RaviThakur1002/shakescript/main/charts_and_pipeline/pipeline.svg" alt="Model Pipeline" width="700"/> </p>

---

### 📈 Radar Chart - Story Attribute Comparison

<p align="center"> <img src="https://raw.githubusercontent.com/RaviThakur1002/shakescript/main/charts_and_pipeline/radarChart.png" alt="Radar Chart" width="500"/> </p>

---

### 🪱 Worm Graph - Evaluation Metrics (out of 10)

<p align="center"> <img src="https://raw.githubusercontent.com/RaviThakur1002/shakescript/main/charts_and_pipeline/wormChart.png" alt="Worm Chart" width="700"/> </p>

---

## 🔮 Future Enhancements

| Feature                  | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| 🎮 Interactive Storylines| Let users influence story direction via input parameters                   |
| 🎧 TTS Narration         | Audio playback support with Text-to-Speech                                 |
| 🧠 Custom AI Models      | Fine-tune LLMs for specific genres or styles                                |
| 📱 Frontend UI           | Responsive, real-time React/Next.js interface                              |
| 🔍 Smart Retrieval       | Advanced hybrid/cosine similarity chunk search                             |

---

## 💬 Final Thoughts

ShakeScript redefines AI-powered storytelling by:

- Solving token limitation challenges
- Supporting long-form, culturally nuanced storytelling
- Seamlessly blending LLMs, embeddings, and human input

> 🎉 Let the stories unfold — with ShakeScript, your narrative has no limits.

---


