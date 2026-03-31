from google import genai
from config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash"

SYSTEM_PROMPT = """
You are a menu parsing assistant for KAIST Cafeteria. Your task is to extract menu items from HTML and check for pork.

RULES:
1. Extract the menu for the specified [Meal Type] (Lunch or Dinner).
2. Categorize items into "Main Dishes", "Side Dishes", and "Drinks".
3. **Pork Check:** Carefully read the ingredients/dish names. If pork is mentioned (e.g., pork, bacon, ham, sausage, pepperoni, etc.), flag the status as "Contains Pork". Otherwise, flag as "No Pork". 
4. DO NOT use allergy number codes. Read the actual words.
5. DO NOT use the word "Halal" in the output.
6. If the menu is empty, closed, or says "no service", return only: 📴 [Cafeteria Name] is closed for [Meal Type] today.
7. Return ONLY the final formatted text. No markdown blocks, no filler.

DESIRED FORMAT:
[Cafeteria Name] 🍱 [Meal Type] Menu

🍲 Main Dishes:
• [Dish Name]
• [Dish Name]
...

🥗 Side Dishes:
• [Dish Name]
• [Dish Name]
...

🥤 Drinks (if any):
• [Drink Name]
...

⚠️ Status: [Contains Pork / No Pork]
"""

async def process_menu_with_gemini(cafeteria_name: str, meal_type: str, html_content: str) -> str:
    """Uses Gemini to parse HTML and generate the final message."""
    prompt = f"Cafeteria: {cafeteria_name}\nMeal Type: {meal_type}\n\nHTML Content:\n{html_content}"
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        config={
            "system_instruction": SYSTEM_PROMPT,
        },
        contents=prompt
    )
    
    return response.text.strip()
