import httpx
from fastapi import APIRouter

router = APIRouter()


@router.get("/mercado/ganado")
async def get_mercado_ganado():
    url = "https://api-cotizaciones.agrofy.com.ar/api/Prices/GetFarmPricesGordo"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://news.agrofy.com.ar/",
        "Accept": "application/json",
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()
