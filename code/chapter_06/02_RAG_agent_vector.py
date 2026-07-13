import uuid
from pathlib import Path

import chromadb
import tiktoken
from agents import Agent, Runner, function_tool  # OpenAI Agents SDK
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ------------------------------------------------------------------
# 1. Load + chunk the script
# ------------------------------------------------------------------
script_text = Path("chapter_06/sample_documents/back_to_the_future.txt").read_text(
    encoding="utf-8"
)


def simple_chunk(text, max_tokens=200):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    words, chunk, chunks = text.split(), [], []
    for w in words:
        if len(tokenizer.encode(" ".join(chunk + [w]))) > max_tokens:
            chunks.append(" ".join(chunk))
            chunk = [w]
        else:
            chunk.append(w)
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks


docs = simple_chunk(script_text, max_tokens=200)

# ------------------------------------------------------------------
# 2. Create (or connect to) a Chroma collection with OpenAI embeddings
# ------------------------------------------------------------------
client = chromadb.PersistentClient(
    path="./chapter_06/chroma_script_store"  # on-disk so we reuse later
)
collection_name = "bttf_script"

# Try to get existing collection first
try:
    collection = client.get_collection(collection_name)
except Exception:
    # Collection doesn't exist, create it without embedding function
    collection = client.create_collection(name=collection_name)

# Populate once (skip if already populated)
if collection.count() == 0:
    collection.add(ids=[str(uuid.uuid4()) for _ in docs], documents=docs)


# ------------------------------------------------------------------
# 3. Define a semantic search tool that queries Chroma
# ------------------------------------------------------------------
@function_tool
def search_script(query: str, top_k: int = 3) -> str:
    res = collection.query(query_texts=[query], n_results=top_k)
    if res and "documents" in res and res["documents"] and res["documents"][0]:
        return "\n\n".join(res["documents"][0])  # combine best chunks
    return "No relevant documents found."


# ------------------------------------------------------------------
# 4. Build the agent
# ------------------------------------------------------------------
agent = Agent(
    name="Script Agent",
    instructions=(
        "You answer questions about the movie *Back to the Future*.\n"
        "When needed, call the `search_script` tool to fetch passages, "
        "then cite or paraphrase them in your answer."
    ),
    tools=[search_script],
)

# ------------------------------------------------------------------
# 5. Ask a question
# ------------------------------------------------------------------
query = "Where does Doc tell Marty to meet him, and at what time?"
result = Runner.run_sync(agent, query)
print("\n--- ANSWER ---\n", result.final_output)

query = "What happens at 1:15AM"
result = Runner.run_sync(agent, query)
print("\n--- ANSWER ---\n", result.final_output)
