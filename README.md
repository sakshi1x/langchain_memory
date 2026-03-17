# Memory Chatty

Memory Chatty is an AI-powered email assistant application that uses Qdrant for persistent, production-grade memory. It leverages `langchain` and `langmem` to provide semantic and episodic memory capabilities.

## Features

- **Semantic and Episodic Memory**: Stores and retrieves examples for better contextual understanding.
- **Persistent Memory**: Powered by Qdrant, memory persists across application restarts.
- **Email Triage**: Classifies emails into `IGNORE`, `NOTIFY`, or `RESPOND` categories.
- **Tools Integration**: Includes tools for writing emails, scheduling meetings, and checking calendar availability.

---

## Installation

### Prerequisites

- Python 3.8+
- `pip` package manager

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

Create a `.env` file in the root directory with the following content:

```env
# Environment variables for the application
QDRANT_PATH=./qdrant_data
EMBEDDING_MODEL=text-embedding-3-small
COLLECTION_NAME=email_assistant_memory
OPENAI_MODEL=gpt-4
OPENAI_KEY=your-openai-api-key
```

Replace `your-openai-api-key` with your OpenAI API key.

---

## Usage

### Step 1: Run the Application

To start the application, run the `main.py` file:

```bash
python main.py
```

### Step 2: Triage Emails

The application will classify emails into one of three categories:

- **IGNORE**: Emails that are not worth responding to.
- **NOTIFY**: Important information that doesn't require a response.
- **RESPOND**: Emails that need a direct response.

### Step 3: Add Examples to Memory

The application automatically stores examples in Qdrant for better contextual understanding in future classifications.

---

## Folder Structure

```
memory_chatty/
├── main.py                # Entry point for the application
├── requirements.txt       # Dependencies
├── config/
│   ├── settings.py        # Configuration settings (e.g., Qdrant paths, API keys)
├── memory/
│   ├── qdrant_store.py    # Qdrant-backed memory implementation
│   ├── memory_manager.py  # High-level memory management logic
├── agent/
│   ├── tools.py           # Tools for the agent (e.g., write_email, schedule_meeting)
│   ├── email_agent.py     # Email assistant logic
├── utils/
│   ├── prompts.py         # Prompt templates for the agent
```

---

## How It Works

1. **Memory Initialization**:
   - The `MemoryManager` initializes a Qdrant-backed vector store.
   - Examples are stored and retrieved using namespaces.

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
