from agent.email_agent import EmailAgent
from agent.tools import write_email, schedule_meeting, check_calendar_availability
from memory.memory_manager import MemoryManager
import json

# Initialize tools and memory manager
tools = [write_email, schedule_meeting, check_calendar_availability]
memory_manager = MemoryManager()

# Create the email agent
agent = EmailAgent(tools=tools, memory_manager=memory_manager)

# Define user profile and rules
profile = {
    "name": "John",
    "full_name": "John Doe",
}

rules = {
    "ignore": "Marketing newsletters, spam emails",
    "notify": "Team updates, project status",
    "respond": "Direct questions, meeting requests",
}

# Load memory examples from test.json
with open("test.json", "r") as file:
    memory_examples = json.load(file)

# Clear memory before saving new examples
print("Clearing memory...")
namespace = ["email_assistant", profile["name"], "examples"]
memory_manager.store.vector_store.delete(namespace)
print("Memory cleared.")

# Debugging: Check if examples are saved to memory
print("Saving examples to memory...")
for example in memory_examples["examples"]:
    memory_manager.save_example(namespace, example["value"])
    print(f"Saved example: {example['value']}")

# Load input emails from input.json
with open("input.json", "r") as input_file:
    input_emails = json.load(input_file)

# Prepare output storage
output_data = {"outputs": []}

# Process each email and log LLM performance
for email in input_emails["emails"]:
    print(f"Processing email: {email['subject']}")
    result = agent.triage_email(email, profile, rules)

    # Debugging: Check memory retrieval during triage
    retrieved_examples = memory_manager.retrieve_examples(namespace, email["email_thread"], limit=3)
    print(f"Retrieved examples: {retrieved_examples}")

    # Convert retrieved examples to a serializable format
    serialized_examples = [
        {
            "metadata": doc.metadata,
            "page_content": doc.page_content
        }
        for doc in retrieved_examples
    ]

    # Check if memory was accessed
    memory_used = len(retrieved_examples) > 0

    # Append result to output data
    output_data["outputs"].append({
        "email": email,
        "result": result.content,
        "memory_used": memory_used,
        "retrieved_examples": serialized_examples
    })

# Save output to output.json
with open("output.json", "w") as output_file:
    json.dump(output_data, output_file, indent=2)

print("Processing complete. Results saved to output.json.")