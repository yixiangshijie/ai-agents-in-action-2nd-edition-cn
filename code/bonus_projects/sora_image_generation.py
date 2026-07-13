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
        name="Image generator",
        instructions="""
        # Image Prompts for "Is Sam Altman Fueling AI Hype or Calling for Caution?"

## 1. Header Image - The Balancing Act
**Prompt:** "Hyper-realistic 3D rendered portrait of a professional businessman in a suit standing on a glowing digital tightrope suspended between two skyscrapers. One skyscraper has holographic projections of rocket ships, dollar signs, and upward trending graphs (representing hype), while the other shows warning triangles, brake symbols, and downward graphs (representing caution). The figure is juggling floating 3D AI brain icons, ChatGPT logos, and bubble-like spheres. Infographic elements include a giant balance scale in the background with 'HYPE' and 'REALITY' labels. Cinematic lighting with neon blue and orange accents. Ultra-detailed, photorealistic rendering with subtle motion blur effects."

## 2. The Hype Machine Section
**Prompt:** "Hyper-realistic 3D scene of a massive, steampunk-inspired 'hype machine' with gears, pistons, and glowing pipes. A professional figure in a suit operates the machine's controls, with holographic projections of ChatGPT logos, marketing icons, and conversation bubbles streaming out of the machine's output funnel. Floating infographic elements show '95% MARKETING' text, megaphone icons, and ascending bar charts. The machine sits on a platform surrounded by miniature 3D rendered office buildings representing different industries. Dramatic studio lighting with golden hour effects, chrome and copper materials, ultra-detailed mechanical components."

## 3. The Reality Check Section  
**Prompt:** "Split-screen hyper-realistic 3D composition: Left side shows the same businessman from previous images pulling a giant red 'EMERGENCY BRAKE' lever attached to a speeding AI-themed train. Right side shows floating holographic warning signs, bubble icons popping, and descending trend lines. The train has 'AI HYPE EXPRESS' written on its side with steam coming from ChatGPT-shaped smokestacks. Infographic overlays include 'BUBBLE WARNING' badges, thermometer showing overheating, and brake light effects. Photorealistic materials with dramatic lighting contrasts between warm (left) and cool blue (right) tones."

## 4. Industry Strikes Back Section
**Prompt:** "Dynamic 3D rendered boardroom scene with multiple professional figures around a holographic conference table. The central Altman-like figure is surrounded by floating speech bubbles containing thumbs-down icons, warning symbols, and 'DISAGREE' text. Other figures have name plates showing 'MARCUS', 'SULEYMAN', 'PICHAI' with their own projected disagreement icons. Above the table, competing infographic projections show conflicting timelines, speed gauges (some showing 'SLOW DOWN', others 'ACCELERATE'), and tug-of-war rope graphics. Cinematic corporate lighting with glass and steel materials, photorealistic textures."

## 5. Hype Fatigue Sets In Section
**Prompt:** "Hyper-realistic 3D rendered conference hall with hundreds of tiny audience figures, all showing exaggerated yawning expressions and 'ZZZ' sleep bubbles floating above their heads. On stage, a presenter gestures at a massive holographic 'AI' logo that's flickering and losing its glow. Floating infographic elements include exhaustion meters, declining attention graphs, and 'OVERLOAD' warning signs. The scene shows scattered coffee cups, dropped phones, and people checking watches. Warm auditorium lighting transitioning to cooler tones, emphasizing fatigue through color psychology."

## 6. The Altman Paradox Section
**Prompt:** "Surreal 3D rendered scene of the same businessman figure split down the middle - left half in bright optimistic colors holding rocket ships and ascending arrows, right half in cautious blues holding shield icons and warning signs. Behind him, a massive Yin-Yang symbol rotates slowly, with 'HYPE' written in the white section and 'CAUTION' in the black section. Floating infographic projections show dual timelines, opposing percentage statistics, and balance beam graphics. The figure stands on a crystal platform with light refracting in multiple directions. High-contrast lighting with dramatic shadows and highlights."

## 7. What This Means for the Future Section
**Prompt:** "Futuristic 3D rendered cityscape with floating holographic interfaces showing 'ROI' calculations, pie charts, and business metrics. A professional figure stands on an elevated platform pointing toward a giant digital clock showing '2025+' while holographic projections display the transformation from 'FOMO' (shown as panicked emoji faces) to 'ROI' (shown as calculator and chart icons). The city below has buildings transforming from chaotic construction to organized, efficient structures. Infographic overlays include roadmap graphics, maturity curves, and success/failure probability meters. Sleek, modern lighting with blue and green tech aesthetics."

## 8. The Bottom Line Section
**Prompt:** "Majestic 3D rendered mountain landscape with two peaks connected by a suspension bridge. One peak labeled 'VISIONARY' has telescope and lightbulb icons floating around it, the other 'REALIST' has magnifying glass and calculator symbols. The businessman figure walks across the bridge carrying a briefcase that projects holographic balance scales. Below, a winding river represents the 'middle path' with various tech company logos flowing like leaves in the current. Infographic elements include convergence arrows, harmony symbols, and a large question mark dissolving into sparkles above. Golden hour lighting with atmospheric depth and photorealistic landscape textures."

---

## Style Consistency Notes:
- **Lighting:** All images use cinematic lighting with warm/cool contrasts
- **Materials:** Mix of photorealistic human figures, chrome/glass tech elements, holographic projections
- **Color Palette:** Consistent blue/orange accent colors with occasional green for positive elements, red for warnings
- **Infographic Elements:** Always floating/projected, never flat - maintain 3D depth
- **Figure Consistency:** Same businessman archetype across all images (professional suit, confident pose)
- **Scale:** Mix of macro (individual focus) and micro (industry-wide) perspectives
- **Symbolism:** Consistent use of arrows (direction), scales (balance), bubbles (hype), gears (machinery of progress)
   """,
        model="gpt-5-mini",
        tools=[
            ImageGenerationTool(
                tool_config={
                    "type": "image_generation",
                    "quality": "high",
                    "model": "gpt-image-1",
                    "size": "1536x1024",
                }
            )
        ],
    )

    images = 8

    with trace("Image generation"):
        for image in range(images):
            try:
                print(f"Generating image {image + 1} of {images}...")
                result = await Runner.run(
                    agent, f"Please create image #{image + 1} of {images}"
                )
                print(result.final_output)
                for item in result.new_items:
                    if (
                        item.type == "tool_call_item"
                        and item.raw_item.type == "image_generation_call"
                        and (img_result := item.raw_item.result)
                    ):
                        os.makedirs("gen_images", exist_ok=True)
                        image_path = os.path.join("gen_images", f"image{image + 1}.png")
                        with open(image_path, "wb") as img_file:
                            img_file.write(base64.b64decode(img_result))
                        open_file(image_path)
            except Exception as e:
                print(f"Error generating image {image + 1}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
