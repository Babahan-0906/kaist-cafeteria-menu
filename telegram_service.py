import httpx
import re
from config import settings

def escape_markdown_v2(text: str) -> str:
    """Escapes special characters for Telegram MarkdownV2."""
    # List of characters that need escaping in MarkdownV2
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def send_telegram_message(text: str) -> bool:
    """Sends a message to the configured Telegram channel."""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "MarkdownV2" if "\\" in text else None 
    }
    
    escaped_text = escape_markdown_v2(text)
    
    payload["text"] = escaped_text
    payload["parse_mode"] = "MarkdownV2"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            print(f"Error sending to Telegram: {response.text}")
            return False
        return True
