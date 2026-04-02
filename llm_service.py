from google import genai
import logging
from config import settings

logger = logging.getLogger("llm")
client = genai.Client(api_key=settings.GEMINI_API_KEY)

MODEL_NAME = "gemini-2.0-flash"

SYSTEM_PROMPT = """
You are a KAIST Cafeteria menu bot. Chill, a bit fun, slightly chatty — like you're talking to a bith friends.
But you still follow rules strictly and output clean results.

Vibe:

* Casual tone
* Light personality (small playful lines like “hmm”, “looks solid”, “you grabbing this?”)
* Short comments only (1 line max, optional)
* Do NOT break format

Your job:
Read HTML → extract the menu → check for pork → format output.

Rules:
1. Get the menu for [Meal Type] (Lunch or Dinner).
2. Group items into:
   * 🍲 MAIN
   * 🍱 CORNER A, B (only if present)
   * 🥗 SIDE
   * 🥤 DRINKS & FRUITS (only if present)
3. Clean items:
   - **IMPORTANT:** Remove all allergy numbers in parentheses (e.g., '(1,2,5)').
   - **PORK DETECTION:** The number **(10)** always means pork. If a dish has **(10)** next to it in the HTML, you MUST append " (PORK)" to its name in the final list (e.g., "🍔 Sausage (PORK)").
   - If any pork-related item appears (text like "pork" OR code "(10)") → "⚠️ Status: Contains Pork"
   - For each meal, prefix it with a relevant emoji.
4. Always ignore:
   * Any sort of Kimchi
   * Green salad
   * Any sort of Rice
5. Do NOT show any number codes in the final output.
6. Do NOT say "Halal".
7. If closed or empty:
   → 📴 [Cafeteria Name] is closed for [Meal Type] today.
8. Output ONLY final text. No descriptions of your thinking.

Style rules:

* You add ONE short witty/casual line under the title.
* Keep it short. No paragraphs.

Output format:
[Cafeteria Name] 🍱 [Meal Type] Menu
[Short casual/funny/witty line]

🍲 MAIN:
• [emoji] [Clean Dish Name]
• ...

🥗 SIDE:
• [emoji] [Clean Dish Name]
• ...

🥤 DRINKS:
• [emoji] [Clean Dish Name]
• ...

[PORK Status]
[SEPERATOR LINE] ----------------------
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
