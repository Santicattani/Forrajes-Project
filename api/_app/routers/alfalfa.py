import asyncio
import httpx
from fastapi import APIRouter

router = APIRouter()

BASE = "https://www.clusterdealfalfa.com.ar/wp-json/heno-cordoba/v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://www.clusterdealfalfa.com.ar/",
    "Accept": "application/json",
}


@router.get("/alfalfa/precios")
async def get_precios_alfalfa():
    async with httpx.AsyncClient(headers=HEADERS, timeout=10) as client:
        cordoba, henif, otras = await asyncio.gather(
            client.get(f"{BASE}/datos/"),
            client.get(f"{BASE}/servicios"),
            client.get(f"{BASE}/otras-pcias"),
        )
        return {
            "cordoba_heno":     cordoba.json(),
            "henificacion":     henif.json(),
            "otras_provincias": otras.json(),
        }
