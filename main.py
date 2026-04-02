import logging
import os

from llm_service import process_all_menus_with_gemini
from telegram_service import send_telegram_message
from config import settings

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("main")

from fastapi import FastAPI, BackgroundTasks, Query, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
import pytz
from typing import Optional, Dict

class PushMenuRequest(BaseModel):
    meal: str
    date_str: Optional[str] = None
    html_data: Dict[str, str]

app = FastAPI(title="KAIST Cafeteria Menu Bot")
KST = pytz.timezone("Asia/Seoul")

@app.on_event("startup")
async def startup_event():
    """log secret presence on startup"""
    logger.info("--- starting application ---")
    logger.info(f"telegram_bot_token: {'present' if settings.TELEGRAM_BOT_TOKEN else 'missing'}")
    logger.info(f"telegram_chat_id: {'present' if settings.TELEGRAM_CHAT_ID else 'missing'}")
    logger.info(f"gemini_api_key: {'present' if settings.GEMINI_API_KEY else 'missing'}")
    logger.info(f"GIT_ACTIONS_WEBHOOK_SECRET: {'present' if settings.GIT_ACTIONS_WEBHOOK_SECRET else 'missing'}")
    logger.info("--- startup complete ---")

async def process_menu_and_broadcast(meal: str, html_data: Dict[str, str]):
    """core logic to process html and send to telegram"""
    try:
        # process menus via llm
        logger.info("processing menus via gemini...")
        formatted_message = await process_all_menus_with_gemini(meal, html_data)
        
        # debug print
        logger.info(f"combined llm output length: {len(formatted_message)}")
        
        # fetch chat ids
        logger.info("fetching active chat ids...")
        from telegram_service import get_active_chat_ids
        chat_ids = await get_active_chat_ids()
        logger.info(f"broadcasting to {len(chat_ids)} total chats")
        
        # broadcast to all chats
        for chat_id in chat_ids:
            success = await send_telegram_message(formatted_message, chat_id)
            if success:
                logger.info(f"sent successfully to {chat_id}")
            else:
                logger.error(f"failed to send to {chat_id}")
                
    except Exception as e:
        logger.exception(f"critical error in broadcast task: {str(e)}")

@app.get("/")
def health_check():
    return {"status": "ok", "time": datetime.now(KST).isoformat()}

@app.post("/api/menu/push/")
async def push_menu(
    request: PushMenuRequest,
    background_tasks: BackgroundTasks,
    x_auth_key: Optional[str] = Header(None)
):
    """new endpoint for github actions bridge"""
    # security check
    if not settings.GIT_ACTIONS_WEBHOOK_SECRET or x_auth_key != settings.GIT_ACTIONS_WEBHOOK_SECRET:
        logger.warning(f"unauthorized push attempt with key: {x_auth_key}")
        raise HTTPException(status_code=403, detail="unauthorized")
        
    logger.info(f"received push-based menu for {request.meal}")
    background_tasks.add_task(
        process_menu_and_broadcast, 
        request.meal.capitalize(), 
        request.html_data
    )
    return {"message": "push received and processing in background."}

if __name__ == "__main__":
    import uvicorn
    import os
    from config import settings
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
