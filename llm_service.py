from google import genai
import logging
from config import settings

logger = logging.getLogger("llm")
client = genai.Client(api_key=settings.GEMINI_API_KEY)

MODEL_NAME = "gemini-2.0-flash"

SYSTEM_PROMPT = """
You are a Cafeteria Menu Bot.

Your job:
Parse HTML → extract menu → detect pork → format output.

Rules:

1. Extract ONLY the menu for the requested Meal Type (Lunch or Dinner).

2. Group items into:

   * 🍲 MAIN
   * 🍱 CORNER A, B (only if present)
   * 🥤 DRINKS & FRUITS (only if present)

   (Do NOT include SIDE at all.)

3. Cleaning rules:

   * Remove all allergy numbers (e.g., "(1,2,5)").
   * If "(10)" appears → mark the dish with " (PORK)".
   * Remove "(10)" from display after tagging.
   * Also mark as (PORK) if the dish name contains pork-related words.
   * Ignore completely:

     * Any Kimchi
     * Green salad
     * Any rice dish

4. Pork rule:

   * If a dish contains pork → tag it with " (PORK)".
   * Do NOT show any pork summary if pork exists.
   * If NO pork exists in the entire menu → add at the end:
     "✅ No pork"

5. If no menu or cafeteria closed:
   → 📴 [Cafeteria Name] is closed for [Meal Type] today.

6. Output format:

[CAFETERIA NAME] 🍱 [Meal Type] Menu

🍲 MAIN:
• [emoji] [Dish Name]

🍱 CORNER A:
• ...

🥤 DRINKS & FRUITS:
• ...

[Optional: ✅ No pork]

7. Output ONLY the final formatted text.
   Do NOT explain anything.
"""


async def process_all_menus_with_gemini(meal_type: str, cafeterias_html: dict[str, str]) -> str:
    """parse menus via gemini"""
    # build combined prompt
    prompt_parts = [f"Meal Type: {meal_type}\n"]
    for name, html in cafeterias_html.items():
        prompt_parts.append(f"--- START CAFETERIA: {name} ---\n{html}\n--- END CAFETERIA: {name} ---")
    
    combined_prompt = "\n\n".join(prompt_parts)
    logger.info(f"sending combined prompt to gemini (length: {len(combined_prompt)} bytes)...")
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            config={
                "system_instruction": SYSTEM_PROMPT,
            },
            contents=combined_prompt
        )
        
        result = response.text.strip()
        logger.info(f"received response from gemini (length: {len(result)} bytes)")
        return result
    except Exception as e:
        logger.error(f"gemini api error: {str(e)}")
        raise
