import os
import httpx


BASE_URL = "https://api.tomorrow.io/v4/weather/forecast"
FIELDS = "temperature,humidity,precipitationProbability,windSpeed"


def evaluar_dia(v: dict) -> dict:
    prob_lluvia = round(v.get("precipitationProbabilityMax", 0))
    humedad = round(v.get("humidityAvg", 0))

    if prob_lluvia < 20 and humedad < 65:
        return {"estado": "ideal", "etiqueta": "Ideal para corte", "razones": []}

    if prob_lluvia < 40 and humedad < 75:
        razones = []
        if prob_lluvia >= 20:
            razones.append(f"Lluvia posible ({prob_lluvia}%)")
        if humedad >= 65:
            razones.append(f"Humedad moderada ({humedad}%)")
        return {"estado": "aceptable", "etiqueta": "Aceptable", "razones": razones}

    razones = []
    if prob_lluvia >= 40:
        razones.append(f"Alta prob. de lluvia ({prob_lluvia}%)")
    if humedad >= 75:
        razones.append(f"Humedad alta ({humedad}%)")
    return {"estado": "no_apto", "etiqueta": "No apto", "razones": razones}


async def obtener_pronostico(latitud: float, longitud: float) -> list[dict]:
    params = {
        "location": f"{latitud},{longitud}",
        "timesteps": "1d",
        "fields": FIELDS,
        "apikey": os.getenv("TOMORROW_API_KEY"),
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

    dias = []
    for entry in data["timelines"]["daily"][:5]:
        v = entry["values"]
        evaluacion = evaluar_dia(v)
        dias.append({
            "fecha": entry["time"][:10],
            "estado": evaluacion["estado"],
            "etiqueta": evaluacion["etiqueta"],
            "razones": evaluacion["razones"],
            "temp_min": round(v.get("temperatureMin", 0)),
            "temp_max": round(v.get("temperatureMax", 0)),
            "humedad": round(v.get("humidityAvg", 0)),
            "prob_lluvia": round(v.get("precipitationProbabilityMax", 0)),
        })
    return dias
