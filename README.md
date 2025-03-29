# **Shakescript - AI-Based Story Creation**  

## **📝 Problem**  
Traditional AI-generated stories often lack **continuity, character consistency, and structured progression** due to **token limitations** in large language models (LLMs). Standard text generation approaches struggle with **long-form storytelling**, making it difficult to maintain coherent multi-episode narratives.  

### **🔹 Challenges in AI Storytelling**  
1️⃣ **Maintaining Narrative Coherence** – Ensuring a seamless connection between episodes.  
2️⃣ **Overcoming Token Limitations** – AI models have a restricted memory window, making it hard to track long-term plots.  
3️⃣ **Character Consistency & Evolution** – Preventing AI from altering personalities or forgetting key character traits.  
4️⃣ **Handling Extended Narratives** – Breaking big stories into **manageable episodic chunks** while keeping the flow intact.  
5️⃣ **Integrating AI Memory** – Ensuring past episodes influence future storytelling without repetition or contradictions.  

---

## **🚀 Shakescript: The AI-Powered Story Generation System**  
Shakescript is a **cutting-edge, AI-driven storytelling pipeline** that generates multi-episode narratives **with structured plot progression, character memory, and long-term consistency**.  

✅ **Accepts a brief prompt** (trope, genre, plotline).  
✅ **Generates a structured multi-episode story** with character depth.  
✅ **Maintains character arcs & world-building** over multiple episodes.  
✅ **Retrieves past story elements** using **memory-aware AI techniques**.  
✅ **Ensures AI-generated content is immersive, engaging, and logically connected.**  

---

## **📂 Project Architecture & Workflow**  

Shakescript follows a **hybrid AI approach**, using **GPT-4o for high-quality episode generation** and **Gemini for metadata extraction, chunk storage, and retrieval**.  

### **1️⃣ User Input & Metadata Extraction (Handled by Gemini)**  
📌 **User provides a prompt** (e.g., "A forbidden love story in the city of Veridion").  
📌 **Gemini AI extracts metadata**:  
   - **Characters** (Name, Role, Relationships).  
   - **Setting & World-building** (City, Environment, Theme).  
   - **Story Structure** (Introduction → Climax → Resolution).  
📌 **Metadata is stored in the relational database (PostgreSQL).**  

---

### **2️⃣ AI Model - Episode Generation (Handled by GPT-4o)**  
📌 **First Episode Generation (GPT-4o)**:  
   - Uses structured **JSON-based prompts** for controlled output.  
   - Retrieves **previously stored metadata** for consistency.  
   - Follows a **predefined episode structure** (Intro, Conflict, Climax, etc.).  

📌 **Subsequent Episode Generation (GPT-4o + Gemini Retrieval)**:  
   - Retrieves **last 2-3 episode summaries**.  
   - Fetches **relevant contextual chunks** from the vector database (Pinecone).  
   - Generates the next episode while **maintaining flow and consistency**.  

📌 **Episode Storage (Handled by Gemini + Relational DB)**:  
   - Episode content is stored in the relational database.  
   - Key chunks are **vectorized & stored in Pinecone** for fast retrieval.  

---

### **3️⃣ Memory Management & Long-Form Continuity (Handled by Gemini)**  
📌 **Retrieves past episode summaries** → Ensures logical progression.  
📌 **Fetches character & setting details** → Prevents AI from altering key traits.  
📌 **Uses a Hybrid Retrieval Model**:  
   - **Relational DB** for structured metadata.  
   - **Vector DB (Pinecone)** for **semantic episode chunk retrieval**.  

---

### **4️⃣ Frontend API & Story Display**  
📌 **FastAPI backend serves generated episodes to a React/Next.js frontend**.  
📌 Users can:  
   - **View structured episodes** with summaries.  
   - **Explore character profiles & key events**.  
   - **Listen to AI-generated stories (TTS support in progress)**.  

---

## **🛠 Technologies & Techniques Used**  

✅ **Natural Language Processing (NLP)**
   - **Named Entity Recognition (NER)** for character & setting extraction.  
   - **Text summarization** to track episode key events.  

✅ **Retrieval-Augmented Generation (RAG)**
   - **Vector Database (Pinecone) for long-term memory retrieval**.  
   - **Semantic search for relevant past episodes**.  

✅ **AI Memory & Context Optimization**
   - **Chunking & Sliding Window Approach** for retrieval.  
   - **Hierarchical embeddings** for characters & settings.  

✅ **Backend & Storage**
   - **FastAPI for API endpoints**.  
   - **PostgreSQL for structured story metadata**.  
   - **Pinecone for vectorized episode storage**.  

✅ **AI Model Usage**
   - **GPT-4o** → Generates full-length, high-quality episodes.  
   - **Gemini** → Handles metadata extraction, chunk storage, retrieval, and pre-processing.  

---

## **🎯 Key Achievements & Innovation**  

✅ **Multi-Episode AI Storytelling** – Ensures logical episode flow.  
✅ **Token Limit Workaround** – Uses **memory-aware retrieval methods**.  
✅ **Character Consistency** – AI **remembers past interactions & relationships**.  
✅ **Advanced Story Structuring** – Generates a well-paced narrative.  

---

## **🔮 Future Enhancements**  

🚀 **Interactive Storytelling** – Users influence AI-driven story decisions.  
🚀 **TTS Narration** – AI-generated audiobook-style narration.  
🚀 **Fine-Tuned AI Models** – Custom-trained models for better storytelling control.  

---

## **💡 Final Thoughts**  

🔹 **Shakescript fully addresses the problem of AI-generated storytelling by integrating memory, retrieval, and structured multi-episode generation.**  
🔹 **Using a hybrid approach (GPT-4o for episodes + Gemini for metadata & retrieval), we ensure high-quality, consistent, and immersive storytelling.**  

🔥 **Shakescript is pushing the boundaries of AI-generated narratives!** 🚀📖  

---
## 📊 System Architecture & Workflow

Below is the **Shakescript AI Storytelling Pipeline**:

![Shakescript Flow Diagram](System_Pipeline.svg)
