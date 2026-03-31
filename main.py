from fastapi import FastAPI, BackgroundTasks, Query
from datetime import datetime
import pytz
from typing import Optional

from scraper import get_all_cafeteria_html
from llm_service import process_menu_with_gemini
from telegram_service import send_telegram_message

app = FastAPI(title="KAIST Cafeteria Menu Bot")

KST = pytz.timezone("Asia/Seoul")

async def run_broadcast_task(meal: str, date_str: str = None):
    """Orchestrates the scraper, LLM, and Telegram broadcast."""
    print(f"Starting broadcast task for {meal} on {date_str or 'today'}")
    
    # 1. Fetch HTML
    html_data = await get_all_cafeteria_html(date_str)
    
    # 2. Process each cafeteria
    for name, html in html_data.items():
        try:
            # Parse with LLM
            formatted_message = await process_menu_with_gemini(name, meal, html)
            
            # Send to Telegram
            success = await send_telegram_message(formatted_message)
            if success:
                print(f"Successfully sent {name} menu to Telegram.")
            else:
                print(f"Failed to send {name} menu to Telegram.")
        except Exception as e:
            print(f"Error processing {name}: {str(e)}")

@app.get("/")
def health_check():
    return {"status": "ok", "time": datetime.now(KST).isoformat()}

@app.post("/trigger")
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
