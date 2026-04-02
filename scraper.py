import asyncio
import logging
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
from config import settings

logger = logging.getLogger("scraper")
KST = pytz.timezone("Asia/Seoul")

WEST_URL = "https://www.kaist.ac.kr/en/html/campus/053001.html?dvs_cd=west"
KAIMARU_URL = "https://www.kaist.ac.kr/en/html/campus/053001.html?dvs_cd=fclt"

async def fetch_menu_html(url: str, date_str: str = None) -> str:
    """fetch menu html via curl"""
    if not date_str:
        date_str = datetime.now(KST).strftime("%Y-%m-%d")
    
    # manual url build
    full_url = f"{url}&stt_dt={date_str}"
    logger.info(f"fetching menu from: {full_url}")
    
    # call curl binary
    process = await asyncio.create_subprocess_exec(
        "curl", "-s", "-L",
        "-H", "User-Agent: Mozilla/5.0",
        full_url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    raw_html = stdout.decode("utf-8", errors="ignore")
    
    if process.returncode != 0 or not raw_html:
        error_msg = stderr.decode().strip()
        logger.error(f"curl failed with code {process.returncode}: {error_msg}")
        return ""
    
    logger.info(f"curl success, received {len(raw_html)} bytes")
    
    # crop to container
    soup = BeautifulSoup(raw_html, "html.parser")
    menu_div = soup.find("div", {"id": "tab_item_1"})
    
    if menu_div:
        logger.info("found menu container tab_item_1")
        return str(menu_div)
    else:
        logger.warning(f"tab_item_1 not found in {url}. raw html snippet: {raw_html[:1000]}")
        return raw_html # fallback to full html

async def get_all_cafeteria_html(date_str: str = None) -> dict:
    """fetch all cafeteria html"""
    # serial fetch for simplicity
    west_html = await fetch_menu_html(WEST_URL, date_str)
    kaimaru_html = await fetch_menu_html(KAIMARU_URL, date_str)
    
    return {
        "West Cafeteria": west_html,
        "KAIMARU": kaimaru_html
    }
