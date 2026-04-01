from fastapi import FastAPI, BackgroundTasks, Query
from datetime import datetime
import pytz
from typing import Optional

from scraper import get_all_cafeteria_html
from llm_service import process_all_menus_with_gemini
from telegram_service import send_telegram_message

app = FastAPI(title="KAIST Cafeteria Menu Bot")

KST = pytz.timezone("Asia/Seoul")

async def run_broadcast_task(meal: str, date_str: str = None):
    """Orchestrates the scraper, LLM, and multi-chat Telegram broadcast."""
    print(f"Starting broadcast task for {meal} on {date_str or 'today'}")
    
    try:
        # 1. Fetch HTML for all cafeterias
        html_data = await get_all_cafeteria_html(date_str)
        
        # 2. Process all menus in a single LLM call
        formatted_message = await process_all_menus_with_gemini(meal, html_data)
        
        # Print for local debugging
        print(f"--- Combined LLM Output for {meal} ---")
        print(formatted_message)
        print("-" * 30)
        
        # 3. Fetch all active chat IDs
        from telegram_service import get_active_chat_ids
        chat_ids = await get_active_chat_ids()
        print(f"Broadcasting to {len(chat_ids)} total chats: {chat_ids}")
        
        # 4. Broadcast to all chats
        for chat_id in chat_ids:
            success = await send_telegram_message(formatted_message, chat_id)
            if success:
                print(f"Sent successfully to {chat_id}")
            else:
                print(f"Failed to send to {chat_id}")
                
    except Exception as e:
        print(f"Critical error in broadcast task: {str(e)}")

@app.get("/")
def health_check():
    return {"status": "ok", "time": datetime.now(KST).isoformat()}

@app.post("/api/menu/")
def trigger_broadcast(
    background_tasks: BackgroundTasks,
    meal: str = Query(..., regex="^(lunch|dinner)$"),
    date: Optional[str] = Query(None, regex="^\d{4}-\d{2}-\d{2}$")
):
    """
    Endpoint triggered by Cloud Scheduler.
    meal: 'lunch' or 'dinner'
    date: YYYY-MM-DD (optional, defaults to today KST)
    """
    background_tasks.add_task(run_broadcast_task, meal.capitalize(), date)
    return {"message": f"Broadcast for {meal} triggered in background."}

if __name__ == "__main__":
    import uvicorn
    import os
    from config import settings
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
