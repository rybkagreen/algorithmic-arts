import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict

async def fetch_url(url: str, timeout: int = 15) -> str:
    """Загрузить HTML страницы."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url, headers={"User-Agent": "AlgorithmicArtsBot/1.0"})
        return resp.text[:5000]  # обрезаем для контекста


async def parse_rss(url: str) -> List[Dict[str, str]]:
    """Распарсить RSS-фид → список {title, link, description}."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url)
    
    try:
        root = ET.fromstring(resp.text)
        items = []
        for item in root.findall(".//item"):
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            description = item.findtext("description", "")
            items.append({
                "title": title,
                "link": link,
                "description": description
            })
        return items
    except Exception:
        return []