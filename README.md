# Memory Chatty

Memory Chatty is an AI-powered email assistant that automatically triages your inbox by classifying emails into **IGNORE**, **NOTIFY**, or **RESPOND** — and gets smarter over time by remembering past decisions.

It uses two types of memory — **Semantic** and **Episodic** — backed by a persistent [Qdrant](https://qdrant.tech/) vector database, powered by `langchain` and `gpt-4o-mini`.

---

## For Non-Technical Readers

### What does this application do?

Imagine you receive hundreds of emails a day. This assistant reads each email and decides:

- 🗑️ **IGNORE** — Spam, promotions, newsletters. Not worth your time.
- 🔔 **NOTIFY** — Team updates, status reports. You should know, but no reply needed.
- 💬 **RESPOND** — Direct questions, meeting requests. You need to act on these.

### How does it "remember"?

This is where memory comes in. There are two kinds of memory in this app:

#### 1. Semantic Memory — "I know facts"

Think of this like a knowledgeable assistant who knows **the rules**: "Marketing emails should be ignored", "Meeting requests need a response."

In this app, semantic memory stores **labeled examples** — past emails and how they were categorized. Before classifying a new email, the assistant looks up the most similar past examples to guide its decision.

> Example: You previously labeled "Special offer on our product!" as IGNORE. When a new promotional email arrives, the assistant finds that memory and uses it to make the same call.

#### 2. Episodic Memory — "I remember what happened"

Think of this like a colleague who says "Last time we got an email like this from Alice, we responded."

In this app, episodic memory stores **the actual outcomes of past triage decisions**. Every time an email is triaged, the result is saved back into memory. So the agent learns from experience in real time, **within the same session**.

> Example: Email 1 gets triaged as RESPOND and saved. When Email 6 arrives with a similar topic, the agent finds Email 1 in memory and uses it as a reference.

### What does "memory used" mean in the output?

- `memory_used: false` — The agent had no relevant past examples to reference. It made its decision with only the rules.
- `memory_used: true` — The agent found similar past emails in memory and used them to guide its classification.

---

## For Technical Readers

### Memory Architecture

| Memory Type  | Psychology Equivalent | What is Stored                         | When Updated                           |
| ------------ | --------------------- | -------------------------------------- | -------------------------------------- |
| **Semantic** | Facts / Knowledge     | Labeled email → category pairs         | Seeded from `test.json` at startup     |
| **Episodic** | Experiences / Events  | Past triage outcomes from this session | After each email is triaged (hot path) |

Both memory types are stored in a **Qdrant vector store** under the namespace `email_assistant|{user}|examples`. Retrieval is similarity-based — the agent embeds the incoming email thread and finds the top-K nearest stored examples using cosine similarity.

### How Memory Flows Through the Application

```
Startup
  │
  ├─ clear_memory(namespace)          ← Wipe stale data from previous runs
  ├─ seed from test.json              ← Semantic memory: pre-labeled examples
  │
  ▼
For each email in input.json:
  │
  ├─ retrieve_examples(namespace, email_thread, limit=3)
  │     └─ Qdrant similarity search filtered by namespace
  │     └─ Returns top-3 most semantically similar past examples
  │
  ├─ Build LLM prompt:
  │     system = TRIAGE_PROMPT (role + rules + retrieved examples)
  │     human  = USER_PROMPT   (email content)
  │
  ├─ LLM classifies → IGNORE / NOTIFY / RESPOND
  │
  ├─ save_example(namespace, {email_thread, category})
  │     └─ Episodic memory: saves this outcome for future emails in the loop
  │
  └─ Append to output.json
```

### Why `memory_used: false` for the first email?

By design. At the start of each run, memory is **cleared** (`clear_memory`) before seeding from `test.json`. However, the **seed-then-retrieve** gap means the first email hits Qdrant immediately after seeding. If the vector index hasn't flushed to disk yet, the search may return 0 results.

This is a known Qdrant local-mode behaviour. In production with a Qdrant server, this is not an issue. For local mode, you can add a small warm-up query after seeding, or simply accept that email 1 uses rules-only while emails 2–6 benefit from episodic memory accumulated during the session.

### Namespace Filtering

LangChain stores metadata as **nested payload** in Qdrant (`metadata.namespace`), not as a top-level field. Both `clear()` and `search()` in `qdrant_store.py` use `FieldCondition(key="metadata.namespace", ...)` to ensure correct namespace isolation.

---

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd memory_chatty
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

Create a `.env` file in the root directory:

```env
QDRANT_PATH=./qdrant_data
EMBEDDING_MODEL=text-embedding-3-small
COLLECTION_NAME=email_assistant_memory
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-openai-api-key
```

---

## Usage

### 1. Add seed examples to `test.json`

These are your **semantic memory** — pre-labeled examples the agent uses as a baseline:

```json
{
  "examples": [
    { "namespace": [...], "key": "ex1", "value": { "email_thread": "Hi, special offer!", "category": "IGNORE" } },
    { "namespace": [...], "key": "ex2", "value": { "email_thread": "Project status report attached.", "category": "NOTIFY" } }
  ]
}
```

### 2. Add emails to triage in `input.json`

```json
{
  "emails": [
    { "author": "...", "to": "...", "subject": "...", "email_thread": "..." }
  ]
}
```

### 3. Run the application

```bash
python main.py
```

### 4. View results in `output.json`

Each result includes:

- `category` — IGNORE / NOTIFY / RESPOND
- `result` — Full LLM response
- `memory_used` — Whether past examples were retrieved
- `retrieved_examples_count` — How many examples were found
- `retrieved_examples` — The actual examples used

---

## Folder Structure

```
memory_chatty/
├── main.py                  # Orchestrator: seed → triage → save → output
├── input.json               # Emails to triage
├── test.json                # Seed examples (semantic memory)
├── output.json              # Triage results with memory tracking
├── requirements.txt
├── config/
│   └── settings.py          # Env-based config (Qdrant path, model names)
├── memory/
│   ├── qdrant_store.py      # Qdrant vector store: put / search (namespace-filtered) / clear
│   └── memory_manager.py    # High-level API: save_example / retrieve_examples / clear_memory
├── agent/
│   ├── email_agent.py       # Core triage logic: retrieves memory → builds prompt → saves result
│   └── tools.py             # LangChain tools: write_email, schedule_meeting, check_calendar
└── utils/
    └── prompts.py           # TRIAGE_PROMPT (system) + USER_PROMPT (human) templates
```

---

## Output Example

```json
{
  "email": { "subject": "Special offer just for you!" },
  "category": "IGNORE",
  "result": "Category: IGNORE",
  "memory_used": true,
  "retrieved_examples_count": 3,
  "retrieved_examples": [...]
}
```

2. **Email Triage**:
   - The `EmailAgent` uses `langchain` to classify emails based on predefined rules.
   - Semantic memory improves classification accuracy over time.

3. **Tools Integration**:
   - Tools like `write_email`, `schedule_meeting`, and `check_calendar_availability` are available to assist with email management.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

- [Qdrant](https://qdrant.tech/)
- [LangChain](https://langchain.com/)
- [LangMem](https://github.com/langchain/langmem)
