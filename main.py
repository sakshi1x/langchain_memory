from agent.email_agent import EmailAgent
from agent.tools import write_email, schedule_meeting, check_calendar_availability
from memory.memory_manager import MemoryManager
import json

# Initialize tools and memory manager
tools = [write_email, schedule_meeting, check_calendar_availability]
memory_manager = MemoryManager()
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

namespace = ["email_assistant", profile["name"], "examples"]

# --- Step 1: Clear existing memory so each run starts fresh ---
print("Clearing memory...")
memory_manager.clear_memory(namespace)
print("Memory cleared.\n")

# --- Step 2: Seed memory with initial examples from test.json ---
with open("test.json", "r") as file:
    memory_examples = json.load(file)

print(f"Seeding {len(memory_examples['examples'])} examples into memory...")
for example in memory_examples["examples"]:
    memory_manager.save_example(namespace, example["value"])
    print(f"  Seeded: [{example['value']['category']}] {example['value']['email_thread'][:60]}")
print("Memory seeded.\n")

# --- Step 3: Load input emails ---
with open("input.json", "r") as input_file:
    input_emails = json.load(input_file)

# --- Step 4: Triage each email, track memory usage, save results ---
output_data = {"outputs": []}

for email in input_emails["emails"]:
    print(f"Processing: {email['subject']}")
    triage = agent.triage_email(email, profile, rules)

    print(f"  Category     : {triage['category']}")
    print(f"  Memory used  : {triage['memory_used']} ({len(triage['retrieved_examples'])} examples retrieved)")
    print(f"  LLM response : {triage['result'][:120]}\n")

    serialized_examples = [
        {"metadata": doc.metadata, "page_content": doc.page_content}
        for doc in triage["retrieved_examples"]
    ]

    output_data["outputs"].append({
        "email": email,
        "category": triage["category"],
        "result": triage["result"],
        "memory_used": triage["memory_used"],
        "retrieved_examples_count": len(triage["retrieved_examples"]),
        "retrieved_examples": serialized_examples,
    })

# --- Step 5: Save results to output.json ---
with open("output.json", "w") as output_file:
    json.dump(output_data, output_file, indent=2)

print("Processing complete. Results saved to output.json.")