import httpx
from datetime import datetime
import pytz

KST = pytz.timezone("Asia/Seoul")

WEST_URL = "https://www.kaist.ac.kr/en/html/campus/053001.html?dvs_cd=west"
KAIMARU_URL = "https://www.kaist.ac.kr/en/html/campus/053001.html?dvs_cd=fclt"

async def fetch_menu_html(url: str, date_str: str = None) -> str:
    """Fetches raw HTML from a KAIST menu page."""
    if not date_str:
        date_str = datetime.now(KST).strftime("%Y-%m-%d")
    
    params = {"stt_dt": date_str}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.text

async def get_all_cafeteria_html(date_str: str = None) -> dict:
    """Fetches HTML from all targeted cafeterias."""
    # We could run these in parallel with asyncio.gather, but keeping it simple for now
    west_html = await fetch_menu_html(WEST_URL, date_str)
    kaimaru_html = await fetch_menu_html(KAIMARU_URL, date_str)
    
    return {
        "West Cafeteria": west_html,
        "KAIMARU": kaimaru_html
    }
