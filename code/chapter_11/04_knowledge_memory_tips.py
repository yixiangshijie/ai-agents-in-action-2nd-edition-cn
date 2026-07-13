from agents import Agent, Runner, SQLiteSession, function_tool

kb = load_vector_kb(  # your FAISS/Weaviate/Chroma wrapper
    embedding_model="text-embedding-3-small",  # choose embeddings deliberately
    index="HNSW",  # ANN (HNSW/IVF)
    shards=["product", "policy", "engineering"],  # shard by domain
)


@function_tool
def retrieve(
    query: str,
    product: str | None = None,
    version: str | None = None,
    date: str | None = None,
    role: str | None = None,
    tenant: str | None = None,
) -> str:
    """Return grounded snippets using metadata filters."""
    return kb.query(
        query=query,
        k=5,
        filters={
            "product": product,
            "version": version,
            "date": date,
            "role": role,
            "tenant": tenant,
        },
    )


@function_tool
def remember(user_id: str, fact: str) -> str:
    """Persist long‑term user fact in vector memory; prune aggressively."""
    kb.upsert(
        text=fact, metadata={"user_id": user_id, "kind": "preference"}, ttl_days=90
    )
    return "ok"


agent = Agent(
    name="Support",
    instructions=(
        "Use ONLY retrieved context; cite chunk ids; if absent say 'I don't know'."
    ),
    tools=[retrieve, remember],
)
session = SQLiteSession("u42-chat")  # short‑term session memory per thread

kb.ingest(
    "docs/*.md",
    chunking="semantic",
    partition_by=["role", "tenant", "product", "version"],
)  # refresh nightly

print(
    Runner.run_sync(
        agent, "Can I use the beta API on v3.2? (tenant=acme)", session=session
    )
)
