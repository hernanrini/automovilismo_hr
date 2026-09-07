import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Mapeo de circuitos de F1 a su huso horario local oficial
CIRCUIT_TIMEZONES = {
    "monza": "Europe/Rome",
    "spa": "Europe/Brussels",
    "zandvoort": "Europe/Amsterdam",
    "singapore": "Asia/Singapore",
    "baku": "Asia/Baku",
    "americas": "America/Chicago",
    "rodriguez": "America/Mexico_City",
    "interlagos": "America/Sao_Paulo",
    "vegas": "America/Los_Angeles",
    "losail": "Asia/Qatar",
    "yas_marina": "Asia/Dubai",
    "silverstone": "Europe/London",
    "catalunya": "Europe/Madrid",
    "monaco": "Europe/Monaco",
    "hungaroring": "Europe/Budapest",
    "red_bull_ring": "Europe/Vienna",
    "albert_park": "Australia/Melbourne",
    "suzuka": "Asia/Tokyo",
    "shanghai": "Asia/Shanghai",
    "miami": "America/New_York",
    "imola": "Europe/Rome",
    "bahrain": "Asia/Bahrain",
    "jeddah": "Asia/Riyadh"
}

def _calcular_hora_local(fecha_utc_str, circuit_id):
    """Convierte la fecha ISO UTC a la hora local del circuito."""
    try:
        dt_utc = datetime.fromisoformat(fecha_utc_str.replace("Z", "+00:00"))
        tz_name = CIRCUIT_TIMEZONES.get(circuit_id, "UTC")
        dt_local = dt_utc.astimezone(ZoneInfo(tz_name))
        tz_code = dt_local.tzname() or ""
        return f"{dt_local.strftime('%H:%M')} Local ({tz_code})".strip()
    except Exception:
        return "Hora Local"

def _nombre_dia(dt, hora_str=""):
    """Genera etiqueta tipo 'VIERNES 04/09' a partir de una fecha."""
    dias = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
    return f"{dias[dt.weekday()]} {dt.day:02d}/{dt.month:02d}"

def obtener_proximas_f1():
    url_f1 = "https://api.jolpi.ca/ergast/f1/current/next.json"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    eventos_f1 = []

    try:
        res = requests.get(url_f1, headers=headers, timeout=10)
        res.raise_for_status()
        races = res.json()["MRData"]["RaceTable"]["Races"]
        if not races:
            return eventos_f1

        carrera1 = races[0]
        ronda1_num = int(carrera1["round"])
        eventos_f1.append(_formatear_evento_f1(carrera1))

        # Segunda carrera futura
        url_siguiente = f"https://api.jolpi.ca/ergast/f1/current/{ronda1_num + 1}.json"
        res2 = requests.get(url_siguiente, headers=headers, timeout=10)
        if res2.status_code == 200:
            races2 = res2.json()["MRData"]["RaceTable"]["Races"]
            if races2:
                eventos_f1.append(_formatear_evento_f1(races2[0]))

        return eventos_f1
    except Exception as e:
        print(f"⚠️ Error scraping F1: {e}")
        return eventos_f1

def _formatear_evento_f1(carrera):
    circuit_id = carrera["Circuit"]["circuitId"]
    sesiones = []

    # Mapeo directo: clave de Jolpica -> nombre a mostrar, destacado o no
    # (incluye formato normal Y formato Sprint; Jolpica solo devuelve
    # las claves que realmente aplican a ese fin de semana)
    sesiones_posibles = [
        ("FirstPractice",     "F1 - Prácticas Libres 1",       False),
        ("SecondPractice",    "F1 - Prácticas Libres 2",       False),
        ("ThirdPractice",     "F1 - Prácticas Libres 3",       False),
        ("SprintQualifying",  "F1 - Clasificación Sprint",     False),
        ("Sprint",            "F1 - Carrera Sprint",           True),
        ("Qualifying",        "F1 - Clasificación",            True),
    ]

    for clave, nombre, destacado in sesiones_posibles:
        if clave in carrera:
            s = carrera[clave]
            utc_str = f"{s['date']}T{s['time']}"
            dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
            sesiones.append({
                "dia": _nombre_dia(dt),
                "nombre": nombre,
                "fechaUtc": utc_str,
                "horaOriginal": _calcular_hora_local(utc_str, circuit_id),
                "destacado": destacado
            })

    # F1 - Carrera Principal (siempre presente)
    fecha_carrera = carrera["date"]
    time_carrera = carrera.get("time", "13:00:00Z")
    if not time_carrera.endswith("Z"):
        time_carrera += "Z"
    utc_carrera = f"{fecha_carrera}T{time_carrera}"
    dt_carrera = datetime.fromisoformat(utc_carrera.replace("Z", "+00:00"))

    sesiones.append({
        "dia": _nombre_dia(dt_carrera),
        "nombre": "F1 - Carrera Principal",
        "fechaUtc": utc_carrera,
        "horaOriginal": _calcular_hora_local(utc_carrera, circuit_id),
        "destacado": True
    })

    return {
        "categoria": "FORMULA 1",
        "categoriaClase": "f1",
        "evento": carrera["raceName"],
        "circuito": carrera["Circuit"]["circuitName"],
        "logoUrl": "",
        "sesiones": sesiones
    }