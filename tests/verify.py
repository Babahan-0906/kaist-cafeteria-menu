import asyncio
from scraper import get_all_cafeteria_html
from telegram_service import escape_markdown_v2

async def test_scraper():
    print("Testing Scraper (requires internet)...")
    try:
        html_data = await get_all_cafeteria_html()
        for name, html in html_data.items():
            print(f"Fetched {len(html)} bytes for {name}")
    except Exception as e:
        print(f"Scraper error: {e}")

def test_telegram_escaping():
    print("\nTesting Telegram MarkdownV2 Escaping...")
    test_str = "West Cafeteria 🍱 Lunch Menu\n\n🍲 Main Dishes:\n• Pork Bulgogi (10.0)\n• Rice\n\n⚠️ Status: Contains Pork!"
    escaped = escape_markdown_v2(test_str)
    print(f"Original: {test_str}")
    print(f"Escaped: {escaped}")
    # Verify common culprits
    assert "\\." in escaped
    assert "\\!" in escaped
    assert "\\(" in escaped
    assert "\\)" in escaped
    print("Escaping looks good!")

if __name__ == "__main__":
    test_telegram_escaping()
    asyncio.run(test_scraper())
