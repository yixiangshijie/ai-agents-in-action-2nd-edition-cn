import asyncio
import base64
import os
import subprocess
import sys
import tempfile

from agents import Agent, ImageGenerationTool, Runner, trace


def open_file(path: str) -> None:
    if sys.platform.startswith("darwin"):
        subprocess.run(["open", path], check=False)  # macOS
    elif os.name == "nt":  # Windows
        os.startfile(path)  # type: ignore
    elif os.name == "posix":
        subprocess.run(["xdg-open", path], check=False)  # Linux/Unix
    else:
        print(f"Don't know how to open files on this platform: {sys.platform}")


async def main():
    agent = Agent(
        name="Slide Image generator",
        instructions="""
# AI Agents Presentation - Playful 3D Image Prompts

## **SLIDE 1: Title Slide**
**Image Prompt:**
"Hyper-realistic 3D render blended with infographic elements showing a playful transformation scene. A cartoon-style person in business attire sits at a desk with scattered prompt papers, looking overwhelmed. Above them, a glowing holographic pathway leads to a confident architect figure wearing a hard hat, surrounded by floating 3D AI agent blueprints and construction tools. Infographic arrows show the transformation journey with icons: 🤖➡️⚡➡️🏗️. Bright, encouraging lighting with cyan and blue accents. Educational popup bubbles explain 'Agency = Decision Power' and 'Autonomous Work Systems'. Playful yet professional atmosphere that makes complex concepts approachable."

---

## **SLIDE 2: Chapter Overview**
**Image Prompt:**
"Hyper-realistic 3D scene of a friendly AI teacher (robotic professor with bowtie) presenting to students using a holographic chalkboard. The board displays four floating 3D textbook sections that open like pop-up books: 1) Agent definition with tiny animated agents dancing, 2) MCP with USB-like connectors linking systems, 3) Five colorful layer cake representing architecture, 4) Multiple agents holding hands in a circle. Infographic elements include progress bars, learning objectives with checkmarks, and floating quiz bubbles. Warm classroom lighting with playful educational atmosphere. Icons float around showing key concepts in a fun, digestible way."

---

## **SLIDE 3: What are AI Agents?**
**Image Prompt:**
"Hyper-realistic 3D render of a playful laboratory scene where three transparent glass containers hold glowing, animated representations. Container 1: A brain made of sparkling circuits with tiny lightning bolts (Agency), Container 2: A Swiss Army knife unfolding into various digital tools (Tools), Container 3: A target with animated arrows hitting bullseyes (Goals). A scientist character with safety goggles combines the containers, creating magical sparkles. Infographic elements include mathematical equations (Agency + Tools + Goals = AI Agent), floating definition bubbles, and comparison charts. Bright, colorful lighting makes complex concepts feel accessible and fun."

---

## **SLIDE 4: Agent vs Assistant**
**Image Prompt:**
"Hyper-realistic 3D scene showing two office cubicles side by side. Left cubicle: An assistant character wearing a 'NEEDS APPROVAL' badge, connected to a computer by a short chain, raising hand for permission before using a single tool. Right cubicle: An agent character wearing a cape labeled 'AUTONOMOUS', freely juggling multiple glowing tools while solving complex puzzles. Infographic comparison chart hovers above showing checkboxes and X's for different capabilities. Speech bubbles show 'May I?' vs 'I'll handle it!'. Playful office lighting with contrasting colors - blues for limitation, bright greens for freedom."

---

## **SLIDE 5: Evolution of LLM Interactions**
**Image Prompt:**
"Hyper-realistic 3D render of a museum evolution exhibit with four dioramas on pedestals connected by a winding pathway. Diorama 1: Simple cave painting of human and AI stick figures. Diorama 2: Medieval scene with AI as translator between human and tool. Diorama 3: Victorian factory with AI operating single machine with human supervisor. Diorama 4: Futuristic scene with AI confidently managing multiple advanced tools independently. Infographic timeline arrows connect each era. A friendly museum guide character points out key differences. Warm museum lighting with educational placards and progress indicators make evolution concept engaging and memorable."

---

## **SLIDE 6: Direct Interaction Pattern**
**Image Prompt:**
"Hyper-realistic 3D scene of two friends having coffee at a cafe table. One represents the user (holding a smartphone), the other represents the LLM (with a glowing brain visible through transparent head). They're engaged in simple conversation with speech bubbles floating between them showing Q&A exchanges. The table is clean with just coffee cups - no tools, gadgets, or external devices. Infographic elements include simplicity icons, conversation flow arrows, and a 'No External Actions' sign with a gentle X mark. Warm, cozy lighting emphasizes the personal, direct nature of basic AI interaction."

---

## **SLIDE 7: Assistant Proxy Pattern**
**Image Prompt:**
"Hyper-realistic 3D scene of a busy restaurant kitchen with three characters. A customer gives their order to a friendly waiter (AI proxy) who then translates and optimizes the order before passing it to a specialized chef (tool). The waiter wears a badge saying 'Request Optimizer' and has a tablet showing translation between customer language and kitchen specifications. Infographic elements include translation bubbles, optimization arrows, and before/after comparison charts. Kitchen setting makes proxy concept relatable - just like waiters help customers communicate with chefs. Bright, bustling atmosphere with educational annotations floating above."

---

## **SLIDE 8: Assistant Pattern**
**Image Prompt:**
"Hyper-realistic 3D scene of a helpful assistant character sitting behind a desk marked 'AI ASSISTANT' with a single red button labeled 'APPROVE.' A user character stands nearby pointing at a tool locked in a glass case with 'NEEDS PERMISSION' signs. The assistant eagerly shows understanding of the tool but cannot activate it without the user pressing the approval button. Infographic elements include permission workflow diagrams, approval checkpoints, and safety protocol icons. Office lighting with amber caution lights around the tool case. Educational bubbles explain 'Smart but Needs Permission' concept in a relatable office scenario."

---

## **SLIDE 9: Agent Pattern**
**Image Prompt:**
"Hyper-realistic 3D scene of a confident conductor character (representing the agent) leading an orchestra of animated tools that play autonomously. The conductor has no approval buttons or permission slips - just confidently directing a symphony of tools: hammer percussion, magnifying glass woodwinds, chart displays in the brass section. Each tool responds independently to the conductor's vision. Infographic elements include autonomy indicators, multi-tasking capability charts, and 'No Human Approval Required' badges. Concert hall lighting with spotlight on the agent, emphasizing leadership and independence in a creative, memorable way."

---

## **SLIDE 10: Thinking Like Agents**
**Image Prompt:**
"Hyper-realistic 3D scene of a detective character (representing agentic thinking) in a study filled with clues, maps, and tools. The detective examines a case file labeled 'USER GOAL,' then moves to a wall covered with connected string diagrams (reasoning), and finally selects appropriate tools from an organized toolkit. Infographic elements include thought bubble progressions, decision tree diagrams, and strategy formulation charts. Sherlock Holmes-style study with warm lamplight creates an atmosphere of intelligent problem-solving. Educational annotations show 'Goal ➡️ Reasoning ➡️ Action' workflow in an engaging detective story format."

---

## **SLIDE 11: The Agent Process Loop**
**Image Prompt:**
"Hyper-realistic 3D scene of a friendly robot character moving through four connected stations in a circular track, like a fun carnival ride. Station 1 (SENSE): Robot uses periscope and radar dish to scan environment. Station 2 (PLAN): Robot sits at strategy table with holographic chess board and battle plans. Station 3 (ACT): Robot operates multiple tool stations simultaneously. Station 4 (LEARN): Robot reviews results on clipboards with gold stars and improvement notes. Colorful carnival atmosphere with infographic signs explaining each station. Bright, playful lighting with educational progress indicators makes the continuous learning cycle feel like an engaging game."

---

## **SLIDE 12: Agents Act with Tools**
**Image Prompt:**
"Hyper-realistic 3D scene of a master craftsperson's workshop where an AI character organizes and registers various magical tools. Tools are displayed on organized pegboards with glowing name tags and instruction manuals. Some tools extend magical energy tendrils that connect to external worlds visible through workshop windows (databases, APIs, applications). The AI character holds a registry book, cataloging each tool's capabilities. Infographic elements include tool classification charts, capability matrices, and connection diagrams. Warm workshop lighting with mystical touches makes tool registration feel like an enchanting craft guild system."

---

## **SLIDE 13: Tool Registration and Usage**
**Image Prompt:**
"Hyper-realistic 3D scene of a magical library with four distinct floors connected by a spiral staircase. Ground floor (Registration): Librarian character stamps tools with 'REGISTERED' seals and files them in catalogs. Second floor (Discovery): Character with magnifying glass examines tool manuals and instruction guides. Third floor (Planning): Strategic character at map table plots which tools to use for different quests. Top floor (Execution): Action character confidently deploys tools to solve problems. Infographic elements include process flow arrows, capability assessment charts, and success metrics. Magical library atmosphere with floating books and glowing inscriptions makes technical process feel like an adventure."

---

## **SLIDE 14: MCP Introduction**
**Image Prompt:**
"Hyper-realistic 3D scene of a universal adapter store where various devices from different eras (old phones, computers, tools) all connect seamlessly through a magical universal hub labeled 'MCP.' A friendly shopkeeper character demonstrates how any agent device can plug into the hub and instantly access any tool, regardless of manufacturer. Infographic elements include compatibility charts, connection diagrams, and 'Works with Everything!' badges. Store setting with bright display lighting makes the universal connectivity concept feel like discovering the perfect adapter that solves all compatibility problems. Educational price tags show benefits: 'No Custom Code Required!'"

---

## **SLIDE 15: Why MCP Matters**
**Image Prompt:**
"Hyper-realistic 3D scene of a before-and-after split showing two developer's desks. Left side (Before MCP): Chaotic desk with tangled cables, multiple incompatible adapters, frustrated developer surrounded by error messages and integration nightmares. Right side (After MCP): Clean, organized desk with single elegant connection hub, happy developer with thumbs up, organized tools working in harmony. Infographic elements include problem-solution comparisons, benefit checklists, and efficiency improvement metrics. Split lighting - harsh fluorescent on left, warm productive light on right. Makes MCP benefits tangible through relatable developer experience scenario."

---

## **SLIDE 16: How MCP Works**
**Image Prompt:**
"Hyper-realistic 3D scene of a four-step assembly line in a friendly tech factory. Step 1: Workers build MCP server like constructing a beautiful toolbox. Step 2: Friendly handshake between agent character and server character (registration). Step 3: Agent character window shopping at server's tool display, reading catalogs (discovery). Step 4: Agent confidently using tools with magical ease, no instruction manuals needed. Infographic elements include step-by-step progress indicators, process flow charts, and 'Plug and Play!' success bubbles. Bright factory lighting with cheerful workers makes technical implementation feel like an efficient, well-organized manufacturing process."

---

## **SLIDE 17: The Five Functional Layers**
**Image Prompt:**
"Hyper-realistic 3D scene of a magnificent five-tier wedding cake being assembled by a master chef character (representing agent architect). Each layer has distinct decorations and functions: Bottom layer (Persona) decorated with identity badges and character traits, Second layer (Tools) with miniature tool figurines, Third layer (Reasoning) with tiny thinking caps and strategy pieces, Fourth layer (Memory) with photo albums and knowledge books, Top layer (Feedback) with quality medals and improvement ribbons. Infographic elements include architectural blueprints, layer function descriptions, and construction progress indicators. Bakery lighting makes complex architecture feel like creating something delightful and beautiful."

---

## **SLIDE 18: Layer 1 - Persona**
**Image Prompt:**
"Hyper-realistic 3D scene of a character creation studio where an AI agent sits in a styling chair getting a makeover. Three stylists work simultaneously: Identity stylist applies role badges and professional uniforms, Behavior stylist adjusts personality dials and communication settings, Instructions stylist writes on a glowing system prompt clipboard. Mirror shows before (generic robot) and after (distinct professional character). Infographic elements include personality sliders, role selection menus, and character stat sheets. Salon lighting with transformation reveal makes persona development feel like an exciting makeover show where AI gets its unique identity."

---

## **SLIDE 19: Layer 2 - Actions & Tools**
**Image Prompt:**
"Hyper-realistic 3D scene of a superhero equipment room where an agent character tries on different tool belts for various missions. Four equipment racks: Task Completion (traditional work tools), Reasoning Support (thinking caps and strategy gadgets), Memory Access (knowledge retrieval devices), Feedback Tools (quality control instruments). Agent enthusiastically tests each tool type, with success indicators and capability meters. Infographic elements include tool category guides, power level meters, and mission success rates. Superhero base lighting with heroic music notes floating around makes tool selection feel like preparing for exciting adventures."

---

## **SLIDE 20: Layer 3 - Reasoning & Planning**
**Image Prompt:**
"Hyper-realistic 3D scene showing two contrasting strategy war rooms. Left room (Single-Path): General character planning linear campaign with single route marked on map, orderly step-by-step battle plans. Right room (Multi-Path): Strategic mastermind with multiple scenario boards, branching decision trees, and parallel strategy options. Both rooms connected by doorway showing they're part of same strategic facility. Infographic elements include strategy comparison charts, decision complexity meters, and outcome probability trees. Military strategy lighting makes planning methodologies feel like choosing between different tactical approaches for mission success."

---

## **SLIDE 21: Layer 4 - Knowledge & Memory**
**Image Prompt:**
"Hyper-realistic 3D scene of a magical library-database hybrid where a librarian character manages six distinct information repositories. Document archives with floating papers, Database servers with glowing data streams, Search terminals with query interfaces, Embedding visualizers showing connected concept webs, Memory banks with experience bottles, RAG systems combining stored knowledge with active queries. Infographic elements include information flow diagrams, retrieval success metrics, and knowledge connection maps. Mystical library lighting with data streams makes information management feel like being a wizard librarian managing magical knowledge repositories."

---

## **SLIDE 22: Layer 5 - Evaluation & Feedback**
**Image Prompt:**
"Hyper-realistic 3D scene of a quality control center with three feedback stations. Internal station: Agent character doing self-reflection with personal improvement mirror and learning journal. External station: Independent quality inspector with official validation stamps and testing equipment. Collaborative station: Team of agent critics providing peer review around feedback table. All stations connected to central improvement hub where agent gets upgraded. Infographic elements include quality metrics, improvement tracking charts, and feedback loop diagrams. Quality control facility lighting makes feedback systems feel like professional quality assurance that ensures excellent results."

---

## **SLIDE 23: Multi-Agent Systems**
**Image Prompt:**
"Hyper-realistic 3D scene of a single overwhelmed character (representing single agent) trying to juggle too many complex tasks, dropping some balls. Scene transitions to show multiple specialized characters (multi-agent system) working together efficiently: one handles scale (bigger challenges), another focuses on specialization (expert tasks), third manages collaboration (team coordination). Team high-fives while single agent looks relieved. Infographic elements include workload distribution charts, specialization benefit graphs, and collaboration effectiveness metrics. Split lighting shows struggle vs success, making multi-agent benefits obvious through relatable teamwork scenario."

---

## **SLIDE 24: Agent-Flow Pattern**
**Image Prompt:**
"Hyper-realistic 3D scene of a cheerful assembly line in a toy factory where four specialized worker characters (agents) create products step-by-step. Agent 1 shapes raw materials, Agent 2 adds features, Agent 3 applies finishing touches, Agent 4 packages final product. Each worker has specialized tools and expertise. Conveyor belt moves products smoothly between stations. Infographic elements include workflow diagrams, specialization charts, and efficiency indicators. Bright factory lighting with happy workers makes sequential specialization feel like a well-orchestrated production line where everyone contributes their unique expertise to create something wonderful."

---

## **SLIDE 25: Agent Orchestration**
**Image Prompt:**
"Hyper-realistic 3D scene of a conductor character (orchestrator agent) leading a symphony where four specialist musicians (worker agents) play different instruments. Conductor doesn't play instruments but coordinates the performance, giving cues and managing the overall composition. Each musician specializes in their instrument but follows conductor's direction. Sheet music shows how conductor delegates musical tasks. Infographic elements include coordination diagrams, task delegation charts, and performance harmony metrics. Concert hall lighting makes hub-and-spoke coordination feel like creating beautiful music through leadership and specialized expertise working in harmony."

---

## **SLIDE 26: Agent Collaboration**
**Image Prompt:**
"Hyper-realistic 3D scene of a collaborative brainstorming room where three agent characters (Developer, QA, Product Manager) sit around a table covered with project materials. They actively discuss, point at shared diagrams, exchange ideas with animated speech bubbles showing cross-communication. Whiteboards show their individual contributions and shared insights. Ideas literally spark and combine in the air above the table. Infographic elements include communication flow diagrams, idea generation metrics, and collaborative outcome measures. Creative workshop lighting makes team collaboration feel like an energetic brainstorming session where diverse expertise creates innovation through active cooperation."

---

## **SLIDE 27: Comparing Multi-Agent Patterns**
**Image Prompt:**
"Hyper-realistic 3D scene of a comparison shopping experience where a customer character examines four different team organization models displayed like product demonstrations. Assembly Line booth shows linear efficiency, Orchestration booth displays centralized coordination, Collaboration booth demonstrates peer-to-peer teamwork, Hybrid booth offers customizable combinations. Each booth has specification sheets showing complexity, control, and cost ratings. Sales representatives explain benefits of each approach. Infographic elements include comparison matrices, decision trees, and suitability guides. Shopping mall lighting makes pattern selection feel like choosing the right organizational structure for specific needs and preferences."

---

## **SLIDE 28: Key Takeaways - Foundation**
**Image Prompt:**
"Hyper-realistic 3D scene of a graduation ceremony where an AI character receives four foundation certificates from a wise professor character. Certificate 1: 'Agency Mastery' showing autonomous decision-making badge. Certificate 2: 'Process Loop Excellence' with continuous learning cycle symbol. Certificate 3: 'Tool Integration Expertise' with external capability connections. Certificate 4: 'MCP Standardization' with universal compatibility badge. Proud family of developer characters claps in audience. Infographic elements include learning achievement charts, skill progression indicators, and foundation mastery levels. Academic ceremony lighting makes foundational concepts feel like important educational milestones worth celebrating and mastering."

---

## **SLIDE 29: Key Takeaways - Architecture**
**Image Prompt:**
"Hyper-realistic 3D scene of an architect character presenting final blueprints for agent systems to an impressed client. Blueprints show: Five-layer architectural plans, Multi-agent collaboration structures, Pattern selection decision guides, Production-ready deployment specifications. Client examines detailed plans with magnifying glass, nodding approvingly. Architectural models demonstrate each concept in miniature. Infographic elements include architectural specifications, implementation roadmaps, and production readiness checklists. Professional architect office lighting makes advanced concepts feel like completing sophisticated engineering plans ready for construction and real-world implementation."

---

## **SLIDE 30: What's Next?**
**Image Prompt:**
"Hyper-realistic 3D scene of an inspiring graduation pathway where a character transforms from 'Prompt Tinkerer' to 'Agent Architect.' Scene shows three milestone gates: Gate 1 (Build) with OpenAI SDK construction tools, Gate 2 (Connect) with MCP integration bridges, Gate 3 (Scale) with multi-agent collaboration platforms. Character walks confidently toward future cityscape filled with autonomous agent systems working harmoniously. Graduation cap transforms into architect's hard hat along the journey. Infographic elements include career progression maps, skill development timelines, and achievement unlock indicators. Inspiring sunrise lighting makes the journey feel like an exciting adventure toward professional mastery and meaningful impact."
""",
        model="o3",
        tools=[
            ImageGenerationTool(
                tool_config={
                    "type": "image_generation",
                    "quality": "high",
                    "model": "gpt-image-1",
                    "size": "1024x1536",
                }
            )
        ],
    )

    images = 30

    with trace("Slide Image generation"):
        for image in range(images):
            print(f"Generating slide image {image + 1} of {images}...")
            result = await Runner.run(
                agent, f"Please create slide image #{image + 1} of {images}"
            )
            print(result.final_output)
            for item in result.new_items:
                if (
                    item.type == "tool_call_item"
                    and item.raw_item.type == "image_generation_call"
                    and (img_result := item.raw_item.result)
                ):
                    os.makedirs("gen_images", exist_ok=True)
                    image_path = os.path.join("gen_images", f"slide{image + 1}.png")
                    with open(image_path, "wb") as img_file:
                        img_file.write(base64.b64decode(img_result))
                    open_file(image_path)


if __name__ == "__main__":
    asyncio.run(main())
