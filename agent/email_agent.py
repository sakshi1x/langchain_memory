from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from utils.prompts import TRIAGE_PROMPT, USER_PROMPT

class EmailAgent:
    def __init__(self, tools, memory_manager):
        self.tools = tools
        self.memory_manager = memory_manager
        self.llm = init_chat_model("openai:gpt-4o-mini")

    def triage_email(self, email, profile, rules):
        namespace = ("email_assistant", profile["name"], "examples")
        examples = self.memory_manager.retrieve_examples(namespace, query=email["email_thread"], limit=3)

        # Format retrieved memory examples for the prompt
        if examples:
            formatted_examples = "\n".join(
                f"- Email: \"{doc.metadata['value']['email_thread']}\" -> Category: {doc.metadata['value']['category']}"
                for doc in examples
                if isinstance(doc.metadata.get("value"), dict) and "category" in doc.metadata["value"]
            ) or "No labeled examples available yet."
        else:
            formatted_examples = "No examples available yet."

        # Build the full structured prompt using TRIAGE_PROMPT + USER_PROMPT
        system_prompt = TRIAGE_PROMPT.format(
            full_name=profile["full_name"],
            ignore_rules=rules["ignore"],
            notify_rules=rules["notify"],
            respond_rules=rules["respond"],
            examples=formatted_examples,
        )

        user_prompt = USER_PROMPT.format(
            author=email["author"],
            to=email["to"],
            subject=email["subject"],
            email_thread=email["email_thread"],
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        chain = prompt | self.llm
        result = chain.invoke({})

        # Parse the category from LLM response
        content_upper = result.content.strip().upper()
        if "IGNORE" in content_upper:
            category = "IGNORE"
        elif "NOTIFY" in content_upper:
            category = "NOTIFY"
        elif "RESPOND" in content_upper:
            category = "RESPOND"
        else:
            category = "UNKNOWN"

        # Save this triage result back to memory so future emails can learn from it
        self.memory_manager.save_example(
            list(namespace),
            {"email_thread": email["email_thread"], "category": category}
        )

        return {
            "result": result.content,
            "category": category,
            "memory_used": len(examples) > 0,
            "retrieved_examples": examples,
        }