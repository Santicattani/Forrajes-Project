import os
from datetime import date
import httpx

BASE_URL = "https://meteostat.p.rapidapi.com/point/daily"
HEADERS = {
    "x-rapidapi-host": "meteostat.p.rapidapi.com",
}


def evaluar_dia_historico(v: dict) -> dict:
    prob_lluvia = v.get("prcp", 0) or 0
    humedad = v.get("rhum", 0) or 0

    # Meteostat no da prob. de lluvia sino mm acumulados
    # Usamos: >2mm como "lluvia posible", >10mm como "lluvia alta"
    if prob_lluvia <= 2 and humedad < 65:
        return {"estado": "ideal", "etiqueta": "Ideal para corte", "razones": []}

    if prob_lluvia <= 10 and humedad < 75:
        razones = []
        if prob_lluvia > 2:
            razones.append(f"Lluvia leve ({prob_lluvia:.1f} mm)")
        if humedad >= 65:
            razones.append(f"Humedad moderada ({humedad:.0f}%)")
        return {"estado": "aceptable", "etiqueta": "Aceptable", "razones": razones}

    razones = []
    if prob_lluvia > 10:
        razones.append(f"Lluvia significativa ({prob_lluvia:.1f} mm)")
    if humedad >= 75:
        razones.append(f"Humedad alta ({humedad:.0f}%)")
    return {"estado": "no_apto", "etiqueta": "No apto", "razones": razones}


async def obtener_historial(
    latitud: float,
    longitud: float,
    fecha_inicio: date,
    fecha_fin: date,
) -> list[dict]:
    params = {
        "lat": latitud,
        "lon": longitud,
        "start": fecha_inicio.isoformat(),
        "end": fecha_fin.isoformat(),
        "alt": 0,
    }
    headers = {**HEADERS, "x-rapidapi-key": os.getenv("METEOSTAT_API_KEY")}

    async with httpx.AsyncClient() as client:
        r = await client.get(BASE_URL, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()

    dias = []
    for entry in data.get("data", []):
        evaluacion = evaluar_dia_historico(entry)
        dias.append({
            "fecha": entry.get("date"),
            "estado": evaluacion["estado"],
            "etiqueta": evaluacion["etiqueta"],
            "razones": evaluacion["razones"],
            "temp_min": entry.get("tmin"),
            "temp_max": entry.get("tmax"),
            "temp_avg": entry.get("tavg"),
            "humedad": entry.get("rhum"),
            "precipitacion_mm": entry.get("prcp"),
            "viento_kmh": entry.get("wspd"),
            "rafaga_max_kmh": entry.get("wpgt"),
            "horas_sol": entry.get("tsun"),
        })
    return dias
