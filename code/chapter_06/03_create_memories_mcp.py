import asyncio

from agents import Agent, Runner
from agents.mcp import MCPServerStdio

# ──────────────────────────────────────────────────────────────
# 1  JSON “memory blocks” we want the agent to execute
# ──────────────────────────────────────────────────────────────
memories = [
    # ---------- ENTITIES -------------------------------------------------
    {
        "name": "create_entities",
        "arguments": {
            "entities": [
                #  people
                {"name": "Marty McFly", "entityType": "Person", "observations": []},
                {
                    "name": "Professor Emmett Brown",
                    "entityType": "Person",
                    "observations": [],
                },
                {"name": "George McFly", "entityType": "Person", "observations": []},
                {
                    "name": "Eileen McFly (née Baines)",
                    "entityType": "Person",
                    "observations": [],
                },
                {"name": "Suzy Parker", "entityType": "Person", "observations": []},
                {"name": "Biff Tannen", "entityType": "Person", "observations": []},
                {"name": "Mr. Arky", "entityType": "Person", "observations": []},
                {
                    "name": "Reginald Washington",
                    "entityType": "Person",
                    "observations": [],
                },
                {"name": "Dick Wilson", "entityType": "Person", "observations": []},
                {
                    "name": "Shemp (organ-grinder monkey)",
                    "entityType": "Person",
                    "observations": [],
                },
                #  places / item
                {
                    "name": "Orpheum Theatre Building",
                    "entityType": "Location",
                    "observations": [],
                },
                {"name": "Brown’s Lab", "entityType": "Location", "observations": []},
                {"name": "Wilson’s Café", "entityType": "Location", "observations": []},
                {
                    "name": "Hill Valley High School",
                    "entityType": "Location",
                    "observations": [],
                },
                {"name": "Power Converter", "entityType": "Item", "observations": []},
            ]
        },
    },
    # ---------- RELATIONS -----------------------------------------------
    {
        "name": "create_relations",
        "arguments": {
            "relations": [
                {
                    "from": "Marty McFly",
                    "to": "George McFly",
                    "relationType": "child_of",
                },
                {
                    "from": "Marty McFly",
                    "to": "Eileen McFly (née Baines)",
                    "relationType": "child_of",
                },
                {"from": "Marty McFly", "to": "Mr. Arky", "relationType": "student_of"},
                {
                    "from": "Marty McFly",
                    "to": "Professor Emmett Brown",
                    "relationType": "mentored_by",
                },
                {
                    "from": "Professor Emmett Brown",
                    "to": "Brown’s Lab",
                    "relationType": "owns_lab",
                },
                {
                    "from": "George McFly",
                    "to": "Eileen McFly (née Baines)",
                    "relationType": "married_to",
                },
                {
                    "from": "Biff Tannen",
                    "to": "George McFly",
                    "relationType": "bullies",
                },
                {
                    "from": "Reginald Washington",
                    "to": "Marty McFly",
                    "relationType": "represents",
                },
                {
                    "from": "Power Converter",
                    "to": "Professor Emmett Brown",
                    "relationType": "invented_by",
                },
                {
                    "from": "Brown’s Lab",
                    "to": "Orpheum Theatre Building",
                    "relationType": "located_in",
                },
            ]
        },
    },
    # ---------- OBSERVATIONS --------------------------------------------
    {
        "name": "add_observations",
        "arguments": {
            "observations": [
                {
                    "entityName": "Power Converter",
                    "contents": [
                        "Marty accidentally pours Coca-Cola into the 30-year-old Power Converter, "
                        "causing a huge voltage spike that convinces Brown the formula works."
                    ],
                },
                {
                    "entityName": "Hill Valley High School",
                    "contents": [
                        "Mr. Arky scolds Marty for expressing curiosity about an atomic blast "
                        "while Suzy passes Marty a flirtatious note."
                    ],
                },
                {
                    "entityName": "George McFly",
                    "contents": [
                        "Biff barges into the McFly kitchen and humiliates George over a burned drill "
                        "while Eileen and Marty watch."
                    ],
                },
            ]
        },
    },
]

# ──────────────────────────────────────────────────────────────
# 2  Minimal agent instructions
#    Every user message *is* a JSON tool payload – just forward it.
# ──────────────────────────────────────────────────────────────
instructions = """
You are a seeding agent.  
Every user message will already be a JSON object with keys `name` and `arguments`.  

Steps:
1. Treat `name` as the exact MCP tool to call.
2. Invoke that tool with `arguments` (wrapped as `input_json=`).
3. Do **not** chat or explain – simply return the tool result.
"""


# ──────────────────────────────────────────────────────────────
# 3  Runner
# ──────────────────────────────────────────────────────────────
async def main() -> None:
    memory_srv = MCPServerStdio(
        name="memory",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory@latest"],
        },
    )

    async with memory_srv:
        agent = Agent(
            name="Seed Memory Agent",
            instructions=instructions,
            mcp_servers=[memory_srv],
        )

        for payload in memories:
            # Each payload goes in as a user message (Runner.run handles wrapping)
            resp = await Runner.run(agent, str(payload))
            print(resp)  # optional: see server acknowledgement


if __name__ == "__main__":
    asyncio.run(main())
