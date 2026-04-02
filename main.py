import logging
import os

from scraper import get_all_cafeteria_html
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

async def run_broadcast_task(meal: str, date_str: str = None):
    """legacy orchestrator that fetches html itself (will likely fail on cloud run)"""
    logger.info(f"starting pull-based broadcast task for {meal} on {date_str or 'today'}")
    try:
        html_data = await get_all_cafeteria_html(date_str)
        await process_menu_and_broadcast(meal, html_data)
    except Exception as e:
        logger.error(f"pull-based fetch failed: {e}")

@app.get("/")
def health_check():
    return {"status": "ok", "time": datetime.now(KST).isoformat()}

@app.post("/api/menu/")
def trigger_broadcast(
    background_tasks: BackgroundTasks,
    meal: str = Query(..., pattern="^(lunch|dinner)$"),
    date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    """legacy endpoint triggered by cloud scheduler"""
    logger.info(f"received pull-based broadcast trigger for {meal}")
    background_tasks.add_task(run_broadcast_task, meal.capitalize(), date)
    return {"message": f"broadcast for {meal} triggered."}

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
