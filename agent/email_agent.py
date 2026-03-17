from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chat_models import init_chat_model
from utils.prompts import TRIAGE_PROMPT, USER_PROMPT
from memory.memory_manager import MemoryManager

class EmailAgent:
    def __init__(self, tools, memory_manager):
        self.tools = tools
        self.memory_manager = memory_manager
        self.llm = init_chat_model("openai:gpt-4o-mini")

    def triage_email(self, email, profile, rules):
        namespace = ("email_assistant", profile["name"], "examples")
        examples = self.memory_manager.retrieve_examples(namespace, query=email["email_thread"], limit=3)

        # New-style prompt
        user_prompt = {
            "email_text": email["email_thread"]
        }

        prompt = PromptTemplate(
            input_variables=["email_text"],
            template="Classify this email: {email_text}"
        )

        chain = prompt | self.llm  # RunnableSequence-style

        result = chain.invoke(user_prompt)
        return result