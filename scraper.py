import httpx
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

import asyncio

KST = pytz.timezone("Asia/Seoul")

WEST_URL = "https://www.kaist.ac.kr/en/html/campus/053001.html?dvs_cd=west"
KAIMARU_URL = "https://www.kaist.ac.kr/en/html/campus/053001.html?dvs_cd=fclt"

async def fetch_menu_html(url: str, date_str: str = None) -> str:
    """Fetches raw HTML using curl and crops it to the relevant menu container."""
    if not date_str:
        date_str = datetime.now(KST).strftime("%Y-%m-%d")
    
    # Construct URL manually for curl
    full_url = f"{url}&stt_dt={date_str}"
    
    # Call the binary directly as requested
    process = await asyncio.create_subprocess_exec(
        "curl", "-s", "-L",
        "-H", "User-Agent: Mozilla/5.0",
        full_url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    raw_html = stdout.decode("utf-8", errors="ignore")
    
    if not raw_html:
        error_msg = stderr.decode().strip()
        print(f"Error calling curl: {error_msg}")
        return ""
    
    # Crop to the targeted container
    soup = BeautifulSoup(raw_html, "html.parser")
    menu_div = soup.find("div", {"id": "tab_item_1"})
    
    if menu_div:
        return str(menu_div)
    else:
        print(f"Warning: tab_item_1 not found in {url}. Returning full HTML.")
        return raw_html # Fallback to full HTML if not found

async def get_all_cafeteria_html(date_str: str = None) -> dict:
    """Fetches HTML from all targeted cafeterias."""
    # We could run these in parallel with asyncio.gather, but keeping it simple for now
    west_html = await fetch_menu_html(WEST_URL, date_str)
    kaimaru_html = await fetch_menu_html(KAIMARU_URL, date_str)
    
    return {
        "West Cafeteria": west_html,
        "KAIMARU": kaimaru_html
    }
