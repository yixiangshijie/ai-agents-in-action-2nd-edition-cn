import asyncio
import base64
import os
import subprocess
import sys

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


async def save_and_open(
    image_bytes: bytes, path: str, open_after_save: bool = True
) -> None:
    # Ensure folder exists and do filesystem + OS operations in a worker thread
    def _write():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(image_bytes)

    await asyncio.to_thread(_write)
    if open_after_save:
        await asyncio.to_thread(open_file, path)


async def generate_one(
    idx: int, total: int, agent: Agent, sem: asyncio.Semaphore
) -> None:
    """
    Generate a single image (idx is 1-based), throttled by `sem`.
    Does network call under the semaphore; saves/opens file outside of it.
    """
    prompt = f"Please create image #{idx} of {total}"
    try:
        print(f"Generating image {idx} of {total}...")
        # Limit only the network/tool call concurrency:
        async with sem:
            result = await Runner.run(agent, prompt)

        # Log model output (may interleave across tasks—normal for concurrency)
        if hasattr(result, "final_output"):
            print(result.final_output)

        # Find the first image tool result and save it
        for item in getattr(result, "new_items", []) or []:
            if (
                getattr(item, "type", None) == "tool_call_item"
                and getattr(getattr(item, "raw_item", None), "type", None)
                == "image_generation_call"
            ):
                img_result = getattr(getattr(item, "raw_item", None), "result", None)
                if img_result:
                    image_bytes = base64.b64decode(img_result)
                    image_path = os.path.join("gen_images", f"image{idx}.png")
                    # Do file I/O and OS open without holding the semaphore
                    await save_and_open(image_bytes, image_path, open_after_save=True)
                    break
    except Exception as e:
        print(f"Error generating image {idx}: {e}")


async def main():
    agent = Agent(
        name="Image generator",
        instructions="""
## Visual Style Header

**Conversational Commerce Diorama Style:** Hyper-realistic 3D miniature diorama aesthetic with soft depth-of-field bokeh, isometric floating platforms and modular scenes, warm ambient lighting with cool tech accents (coral orange + electric teal), matte clay-render characters with simplified friendly faces, mixed with crisp 2D vector infographic overlays and clean sans-serif labels, premium product photography lighting quality, solid gradient backgrounds (deep navy to soft purple), cinematic tilt-shift miniature effect.

---

## Image Prompts

---

### **1. HERO IMAGE — "Shopping Becomes a Conversation"**

**Concept:** The transformation from clicking to chatting — AI as your personal shopping companion

**Prompt:**
Conversational Commerce Diorama Style: Hyper-realistic 3D miniature diorama aesthetic with soft depth-of-field bokeh, isometric floating platforms, warm ambient lighting with cool tech accents (coral orange + electric teal), matte clay-render characters with simplified friendly faces, mixed with crisp 2D vector infographic overlays and clean sans-serif labels, solid gradient background (deep navy to soft purple), cinematic tilt-shift miniature effect.

A split-scene 3D diorama showing the evolution of shopping. LEFT SIDE (fading/desaturated): A tiny clay-render person hunched over a laptop, surrounded by dozens of floating browser windows, shopping carts, and pop-up ads creating visual chaos — labeled "2024: Click. Search. Scroll. Repeat." RIGHT SIDE (vibrant/glowing): The same person relaxed on a couch, casually chatting with a friendly floating AI orb companion that has a warm coral glow and simple happy expression, speech bubbles between them showing "I need a winter jacket" → "Found 3 perfect matches!", a single elegant product card floating nearby. A large curved arrow connects both sides labeled "THE SHIFT." Playful elements: a tiny robot butler carrying shopping bags in background, a frustrated mouse cursor character walking away on left side, confetti particles around the AI orb. Clean 2D label at bottom: "$1 TRILLION MARKET BY 2030." No transparent background.

---

### **2. SECTION: "The Tech Tipping Point — Why Now?"**

**Concept:** Three forces converging to enable conversational commerce (costs + interfaces + regulations)

**Prompt:**
Conversational Commerce Diorama Style: Hyper-realistic 3D miniature diorama aesthetic with soft depth-of-field bokeh, isometric floating platforms, warm ambient lighting with cool tech accents (coral orange + electric teal), matte clay-render characters, mixed with crisp 2D vector infographic overlays, solid gradient background (deep navy to soft purple), cinematic tilt-shift miniature effect.

Three distinct floating island platforms arranged in a triangle, converging toward a glowing central point labeled "TIPPING POINT 2025." ISLAND 1 (bottom-left): A crumbling tower of gold coins dramatically shrinking with a downward arrow, tiny shocked accountant character watching — labeled "💰 COSTS: 1000x CHEAPER." ISLAND 2 (bottom-right): A friendly smart speaker, smartphone, and AR glasses arranged together with colorful sound waves and visual recognition beams emanating outward, small character speaking naturally to devices — labeled "🎤 INTERFACES: VOICE + VISION." ISLAND 3 (top): A shield emblem with EU and US flags, glowing green checkmark, tiny official character stamping documents — labeled "📋 REGULATIONS: CLEAR RULES." Glowing teal energy streams flow from all three islands into the central convergence point which pulses with light. Playful elements: a tiny rocket launching from the center point, miniature "OPEN" sign lighting up. No transparent background.

---

### **3. SECTION: "From Search Engines to Answer Engines"**

**Concept:** The funnel collapse — from 100 results to 1 conversation

**Prompt:**
Conversational Commerce Diorama Style: Hyper-realistic 3D miniature diorama aesthetic with soft depth-of-field bokeh, isometric floating platforms, warm ambient lighting with cool tech accents (coral orange + electric teal), matte clay-render characters, mixed with crisp 2D vector infographic overlays, solid gradient background (deep navy to soft purple), cinematic tilt-shift miniature effect.

A dramatic visual comparison showing funnel transformation. LEFT: A tall, complex Rube Goldberg machine made of miniature platforms — a tiny person at top drops a "search query" ball that bounces through "100 RESULTS" (chaotic pile of product boxes), then "BROWSE & COMPARE" (exhausted character with magnifying glass), then "ADD TO CART," finally reaching "CHECKOUT" at bottom — total journey labeled "OLD WAY: 47 CLICKS." RIGHT: A simple elegant slide where a character speaks into a glowing AI interface at top, speech bubble says "Best budget laptop?", and a single perfect product box glides smoothly down a golden path directly to a happy customer at bottom — labeled "NEW WAY: 1 CONVERSATION." A large "VS" divides the scenes. Playful elements: tiny product boxes with cartoon faces looking relieved on the right side, a "CLOSED" sign on an old search bar, streamers celebrating the simple path. No transparent background.

---

### **4. SECTION: "The New Ecosystem — Platform Power Shift"**

**Concept:** AI agents become the new gatekeepers between consumers and retailers

**Prompt:**
Conversational Commerce Diorama Style: Hyper-realistic 3D miniature diorama aesthetic with soft depth-of-field bokeh, isometric floating platforms, warm ambient lighting with cool tech accents (coral orange + electric teal), matte clay-render characters, mixed with crisp 2D vector infographic overlays, solid gradient background (deep navy to soft purple), cinematic tilt-shift miniature effect.

A medieval castle gate reimagined as a futuristic AI portal. CENTER: A large ornate gateway structure with a friendly giant AI assistant face embedded in the arch (glowing teal eyes, welcoming expression), labeled "THE NEW GATEKEEPER." LEFT of gate: A single happy clay-render consumer character with shopping bag, speech bubble showing simple request. RIGHT of gate: Multiple colorful storefronts (miniature shops representing Amazon, small businesses, brands) all trying to get the AI's attention, some with "PICK ME!" signs. Above the gate: A crown floating, with text "WHO CONTROLS THE CONVERSATION?" Golden streams of transactions flow through the gate. At bottom: Three protocol badges labeled "MCP," "AP2," "ACP" like passport stamps. Playful elements: a tiny traditional search bar character crying in the corner, a small toll booth with "2% FEE" sign, one shop owner polishing their data to look presentable. No transparent background.

---

### **5. SECTION: "Winners and Losers"**

**Concept:** Clear visualization of who benefits vs. who's disrupted by agentic commerce

**Prompt:**
Conversational Commerce Diorama Style: Hyper-realistic 3D miniature diorama aesthetic with soft depth-of-field bokeh, isometric floating platforms, warm ambient lighting with cool tech accents (coral orange + electric teal), matte clay-render characters, mixed with crisp 2D vector infographic overlays, solid gradient background (deep navy to soft purple), cinematic tilt-shift miniature effect.

A dramatic seesaw/balance scale diorama. LEFT SIDE (rising up, bathed in warm golden light): Platform labeled "WINNERS" with celebrating clay characters — a consumer holding money saved (piggy bank overflowing), an AI platform character collecting small coins, a brand mascot holding a glowing "QUALITY DATA" trophy. Each has floating labels: "CONSUMERS: Better Prices," "AI PLATFORMS: Transaction Fees," "Data-Ready Brands." RIGHT SIDE (sinking down, slightly shadowed): Platform labeled "DISRUPTED" with worried characters — an ad billboard character cracking ($70B text fading), a traditional SEO character with broken keywords, a walled-garden fortress character looking defensive. Labels: "Ad Revenue: Threatened," "Old SEO: Obsolete," "Closed Platforms: Fighting Back." The fulcrum is shaped like a shopping cart. Playful elements: tiny dollar bills floating from right to left, a small "ADAPT OR..." warning sign, a life preserver thrown toward the sinking side. No transparent background.

---

### **6. SECTION: "The Ethical Checklist"**

**Concept:** The four pillars of responsible AI commerce (Transparency, Privacy, Fairness, Accountability)

**Prompt:**
Conversational Commerce Diorama Style: Hyper-realistic 3D miniature diorama aesthetic with soft depth-of-field bokeh, isometric floating platforms, warm ambient lighting with cool tech accents (coral orange + electric teal), matte clay-render characters, mixed with crisp 2D vector infographic overlays, solid gradient background (deep navy to soft purple), cinematic tilt-shift miniature effect.

A Greek temple structure with four glowing pillars, each a different color, supporting a roof labeled "TRUST." PILLAR 1 (coral): Transparency — a friendly AI character with a visible "I'M AN AI" name badge, speech bubble showing "Sponsored" label. PILLAR 2 (teal): Privacy — a secure vault door with a lock, tiny user data documents safe inside. PILLAR 3 (gold): Fairness — balanced scales with "no manipulation" symbol, protected user character. PILLAR 4 (green): Accountability — a human customer service rep standing next to an AI, "HUMAN AVAILABLE" sign glowing. At the base: An FTC badge and EU flag as foundation stones. Above the temple roof: A glowing heart-shaped trust meter showing "HIGH." Playful elements: a tiny robot checking boxes on a clipboard, a small detective character with magnifying glass auditing, a "NO DARK PATTERNS" stop sign. No transparent background.

---

### **7. SECTION: "What Businesses Should Do Now"**

**Concept:** Three actionable steps — Pilot, Fix Data, Build Trust

**Prompt:**
Conversational Commerce Diorama Style: Hyper-realistic 3D miniature diorama aesthetic with soft depth-of-field bokeh, isometric floating platforms, warm ambient lighting with cool tech accents (coral orange + electric teal), matte clay-render characters, mixed with crisp 2D vector infographic overlays, solid gradient background (deep navy to soft purple), cinematic tilt-shift miniature effect.

A rocket launch pad scene with three sequential preparation stages, numbered 1-2-3 ascending toward a launching rocket. STAGE 1 (ground level): "START SMALL" — a tiny scientist character running a small experiment with a mini chatbot in a test tube, beakers and pilot program materials around, label "🧪 PILOT PROJECTS." STAGE 2 (middle platform): "FIX YOUR DATA" — a mechanic character polishing and organizing messy product cards into neat, glowing structured data containers, scattered "schema markup" tools, label "📊 AI-READY DATA." STAGE 3 (upper platform): "BUILD TRUST" — a construction crew placing final pieces on a handshake monument between human and AI characters, "CONFIRM PURCHASE?" dialog box, label "🤝 HUMAN OVERSIGHT." The rocket at top is labeled "READY FOR 2025" with exhaust starting to fire. Playful elements: a checklist floating with satisfying checkmarks, a tiny "EASY BUTTON" being pressed, a small competitor character falling behind in background. No transparent background.

---

### **8. SECTION: "The Bottom Line — The Future Is Conversational"**

**Concept:** The spectrum of AI shopping adoption — routine purchases vs. discovery shopping

**Prompt:**
Conversational Commerce Diorama Style: Hyper-realistic 3D miniature diorama aesthetic with soft depth-of-field bokeh, isometric floating platforms, warm ambient lighting with cool tech accents (coral orange + electric teal), matte clay-render characters, mixed with crisp 2D vector infographic overlays, solid gradient background (deep navy to soft purple), cinematic tilt-shift miniature effect.

A horizontal spectrum/slider visualization as a 3D diorama landscape. LEFT SIDE (fully AI zone, glowing teal): Mundane products floating — groceries, batteries, electronics, household items — with happy AI robots efficiently sorting and delivering them, a satisfied lazy customer on couch, label "🤖 AI-PERFECT: Routine Purchases." RIGHT SIDE (human zone, warm coral): Fashion items, home décor, art, gifts — with a human browsing joyfully through a beautiful boutique, touching fabrics, trying things on, label "👤 HUMAN JOY: Discovery Shopping." CENTER: A friendly slider/dial that a consumer character is adjusting, showing they control the balance. Above the whole scene: "THE FUTURE: YOU CHOOSE" in elegant text. A timeline arrow at bottom shows "2025 → 2030" with adoption growing. Playful elements: a tiny AI looking confused at a fashion runway, a human character happily ignoring an AI suggestion for a gift, a "Best of Both Worlds" trophy in the center. No transparent background.

---

## Summary

| # | Section | Core Concept |
|---|---------|--------------|
| 1 | Hero | Shopping evolution: clicking → chatting |
| 2 | Tech Tipping Point | Three converging forces enable 2025 moment |
| 3 | Search to Answer | Funnel collapse: 100 results → 1 conversation |
| 4 | New Ecosystem | AI agents as new retail gatekeepers |
| 5 | Winners & Losers | Who benefits vs. who's disrupted |
| 6 | Ethical Checklist | Four pillars of trust |
| 7 | Business Action | Three steps: Pilot, Data, Trust |
| 8 | Bottom Line | Spectrum of human vs. AI shopping |

Each prompt includes the style header, educational labels visible in 3-5 seconds, and 2-3 playful supporting elements!
""",
        model="gpt-5.2",
        tools=[
            ImageGenerationTool(
                tool_config={
                    "type": "image_generation",
                    "quality": "high",
                    "model": "gpt-image-1.5",
                    "size": "1536x1024",
                }
            )
        ],
    )

    total_images = 8
    # Limit how many generations run at once (override via IMG_CONCURRENCY env var)
    concurrency = int(os.environ.get("IMG_CONCURRENCY", "5"))
    concurrency = max(1, min(concurrency, total_images))
    sem = asyncio.Semaphore(concurrency)

    with trace("Image generation"):
        tasks = [
            asyncio.create_task(generate_one(i + 1, total_images, agent, sem))
            for i in range(total_images)
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
