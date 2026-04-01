import httpx
import re
from config import settings

def escape_markdown_v2(text: str) -> str:
    """Escapes special characters for Telegram MarkdownV2."""
    # List of characters that need escaping in MarkdownV2
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def get_active_chat_ids() -> set[str]:
    """Fetches unique chat IDs from the bot's recent updates."""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
    chat_ids = set()
    
    # Always include the default chat ID from .env as a primary target
    if settings.TELEGRAM_CHAT_ID:
        chat_ids.add(settings.TELEGRAM_CHAT_ID)
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                for update in data.get("result", []):
                    # Check for messages (private or group)
                    if "message" in update:
                        chat_ids.add(str(update["message"]["chat"]["id"]))
                    # Check for channel posts
                    elif "channel_post" in update:
                        chat_ids.add(str(update["channel_post"]["chat"]["id"]))
                    # Check for membership updates
                    elif "my_chat_member" in update:
                        chat_ids.add(str(update["my_chat_member"]["chat"]["id"]))
    except Exception as e:
        print(f"Error fetching updates: {e}")
        
    return chat_ids

async def send_telegram_message(text: str, chat_id: str) -> bool:
    """Sends a message to a specific Telegram chat ID."""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    escaped_text = escape_markdown_v2(text)
    
    payload = {
        "chat_id": chat_id,
        "text": escaped_text,
        "parse_mode": "MarkdownV2"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            print(f"Error sending to {chat_id}: {response.text}")
            return False
        return True
