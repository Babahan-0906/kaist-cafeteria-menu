import httpx
import re
import logging
from config import settings

logger = logging.getLogger("telegram")

def escape_markdown_v2(text: str) -> str:
    """escape markdown v2"""
    # characters to escape
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def get_active_chat_ids() -> set[str]:
    """fetch active chat ids"""
    logger.info("fetching updates from telegram...")
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
    chat_ids = set()
    
    # add default chat id
    if settings.TELEGRAM_CHAT_ID:
        chat_ids.add(settings.TELEGRAM_CHAT_ID)
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                updates = data.get("result", [])
                logger.info(f"received {len(updates)} updates from telegram")
                for update in updates:
                    # handle messages
                    if "message" in update:
                        chat = update["message"]["chat"]
                        chat_type = chat.get("type")
                        # skip private chats
                        if chat_type != "private":
                            chat_ids.add(str(chat["id"]))
                    # handle channel posts
                    elif "channel_post" in update:
                        chat = update["channel_post"]["chat"]
                        chat_ids.add(str(chat["id"]))
                    # handle membership updates
                    elif "my_chat_member" in update:
                        chat = update["my_chat_member"]["chat"]
                        chat_type = chat.get("type")
                        if chat_type != "private":
                            chat_ids.add(str(chat["id"]))
            else:
                logger.error(f"failed to fetch updates: {response.status_code} {response.text}")
    except Exception as e:
        logger.error(f"exception fetching updates: {e}")
        
    return chat_ids

async def send_telegram_message(text: str, chat_id: str) -> bool:
    """send telegram message"""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    escaped_text = escape_markdown_v2(text)
    
    payload = {
        "chat_id": chat_id,
        "text": escaped_text,
        "parse_mode": "MarkdownV2"
    }
    
    logger.info(f"sending message to chat {chat_id}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                data = response.json()
                # handle upgraded group chats
                if response.status_code == 400 and "parameters" in data:
                    new_id = data["parameters"].get("migrate_to_chat_id")
                    if new_id:
                        logger.info(f"chat {chat_id} upgraded! migrating to {new_id}...")
                        payload["chat_id"] = str(new_id)
                        # retry with new id
                        response = await client.post(url, json=payload)
                        if response.status_code == 200:
                            logger.info(f"successfully sent to {new_id} after migration")
                            return True

                logger.error(f"telegram api error for {chat_id}: {response.status_code} {response.text}")
                return False
            
            logger.info(f"successfully sent message to {chat_id}")
            return True
    except Exception as e:
        logger.error(f"exception sending to {chat_id}: {e}")
        return False

async def leave_chat(chat_id: str) -> bool:
    """make bot leave a specific chat via telegram api"""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/leaveChat"
    payload = {"chat_id": chat_id}
    
    logger.info(f"making bot leave chat: {chat_id}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                logger.info(f"successfully left chat: {chat_id}")
                return True
            else:
                logger.error(f"failed to leave chat {chat_id}: {response.text}")
                return False
    except Exception as e:
        logger.error(f"exception while leaving chat {chat_id}: {e}")
        return False
