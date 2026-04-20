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

0. IMPORTANT: Prioritize the menu for "Today's Date (KST)" provided in the prompt. Match it with the date/day found in the HTML (e.g., "04/20(Mon)").

1. Extract ONLY the menu for the requested Meal Type (Lunch or Dinner). 
   NOTE: The HTML is often messy and fragmented (e.g., "Perilla Seed Duclack Rice"). Try your best to reconstruct the full dish names from the fragments.

2. Group items into:

   * 🍲 MAIN
   * 🥤 DRINKS & FRUITS (only if present)

   (Do NOT include CORNER A, B, or any other sub-headers. Put all main dishes under 🍲 MAIN).
   (Do NOT include SIDE at all.)

3. Cleaning rules:

   * Remove all allergy numbers (e.g., "(1,2,5)").
   * If "(10)" appears → mark the dish with " (PORK)".
   * Also mark as (PORK) if the dish name contains pork-related words: Pork, Ham, Bacon, Sausage, Pepperoni, Cutlet (unless specified otherwise).
   * Remove "(10)" from display after tagging.
   * Ignore completely:
     * Any Kimchi
     * Green salad
     * Any rice dish (e.g., White Rice, Brown Rice)

4. Pork rule:

   * If a dish contains pork → tag it with " (PORK)".
   * If AT LEAST ONE dish in the entire cafeteria menu (MAIN, CORNER A, B, etc.) has (PORK) → Do NOT add "✅ No pork".
   * If NO dish in the entire cafeteria menu contains pork → add at the end: "✅ No pork"

5. If no menu is found, or it says "No menu", or the cafeteria is clearly closed for that meal:
   → 📴 [Cafeteria Name] is closed for [Meal Type] today.

6. Output format:

[CAFETERIA NAME] 🍱 [Meal Type] Menu

🍲 MAIN:
• [emoji] [Dish Name]

🥤 DRINKS & FRUITS:
• ...

[Optional: ✅ No pork]

(If multiple cafeterias, just append them one after another without any extra separators, horizontal lines, or "---" lines).

7. Output ONLY the final formatted text. Do NOT explain anything.
"""


async def process_all_menus_with_gemini(meal_type: str, cafeterias_html: dict[str, str], current_date: str) -> str:
    """parse menus via gemini"""
    # build combined prompt
    prompt_parts = [
        f"Today's Date (KST): {current_date}",
        f"Requested Meal Type: {meal_type}\n"
    ]
    for name, html in cafeterias_html.items():
        prompt_parts.append(f"--- START CAFETERIA: {name} ---\n{html}\n--- END CAFETERIA: {name} ---")
    
    combined_prompt = "\n\n".join(prompt_parts)
    logger.info(f"--- PROMPT SENT TO GEMINI ---\n{combined_prompt}\n--- END PROMPT ---")
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
        logger.info(f"--- RESPONSE FROM GEMINI ---\n{result}\n--- END RESPONSE ---")
        logger.info(f"received response from gemini (length: {len(result)} bytes)")
        return result
    except Exception as e:
        logger.error(f"gemini api error: {str(e)}")
        raise
