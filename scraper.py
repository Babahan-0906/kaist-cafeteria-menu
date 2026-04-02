import logging
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
from config import settings
from curl_cffi.requests import AsyncSession

logger = logging.getLogger("scraper")
KST = pytz.timezone("Asia/Seoul")

WEST_URL = "https://www.kaist.ac.kr/en/html/campus/053001.html?dvs_cd=west"
KAIMARU_URL = "https://www.kaist.ac.kr/en/html/campus/053001.html?dvs_cd=fclt"

async def fetch_menu_html(url: str, date_str: str = None) -> str:
    """fetch menu html via curl-impersonate"""
    if not date_str:
        date_str = datetime.now(KST).strftime("%Y-%m-%d")
    
    # manual url build
    try:
        async with AsyncSession() as s:
            # impersonate modern human chrome browser
            response = await s.get(full_url, impersonate="chrome120", timeout=30)
            
            if response.status_code != 200:
                logger.error(f"fetch failed with status {response.status_code}")
                # log snippet of error page if needed
                if settings.DEBUG_SCRAPER:
                    logger.debug(f"error response snippet: {response.text[:500]}")
                return ""
                
            raw_html = response.text
            
    except Exception as e:
        logger.error(f"exception during fetch from {url}: {e}")
        return ""
    
    logger.info(f"fetch success, received {len(raw_html)} bytes")
    
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
