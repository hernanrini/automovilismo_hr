import requests
from datetime import datetime, timedelta

def obtener_proximas_motogp():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    eventos_motogp = []
    
    try:
        url_seasons = "https://api.motogp.pulselive.com/motogp/v1/results/seasons"
        res = requests.get(url_seasons, headers=headers, timeout=10)
        res.raise_for_status()
        seasons = res.json()
        
        season_id = None
        for s in seasons:
            if s.get("current") is True:
                season_id = s.get("id")
                break
        
        if not season_id and seasons:
            season_id = seasons[0]["id"]
            
        if not season_id:
            return eventos_motogp

        url_events = f"https://api.motogp.pulselive.com/motogp/v1/results/events?seasonUuid={season_id}"
        res_events = requests.get(url_events, headers=headers, timeout=10)
        res_events.raise_for_status()
        events = res_events.json()
        print(f"MotoGP API: Se encontraron {len(events)} eventos en total.")

        for ev in events:
            nombre_gp = ev.get("name", "")
            # Descartamos los entrenamientos de pretemporada (tests)
            if ev.get("test") is True or "TEST" in nombre_gp.upper():
                continue

            evento_formateado = _formatear_evento_motogp(ev)
            if evento_formateado and evento_formateado.get("sesiones"):
                eventos_motogp.append(evento_formateado)

        print(f"MotoGP API: {len(eventos_motogp)} eventos procesados correctamente.")
        return eventos_motogp
    except Exception as e:
        print(f"⚠️ Error scraping MotoGP: {e}")
        return eventos_motogp

def _nombre_dia(dt):
    dias = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
    return f"{dias[dt.weekday()]} {dt.day:02d}/{dt.month:02d}"

def _formatear_evento_motogp(ev):
    # Usamos el sponsored_name si está disponible para que muestre el nombre comercial del GP
    nombre_gp = ev.get("sponsored_name") or ev.get("name", "Gran Premio de MotoGP")
    circuito_info = ev.get("circuit", {})
    nombre_circuito = circuito_info.get("name", "Circuito MotoGP")
    
    sesiones = []

    # Claves exactas devueltas por la API de MotoGP
    date_start_str = ev.get("date_start")
    date_end_str = ev.get("date_end")

    if date_start_str and date_end_str:
        try:
            dt_fin = datetime.strptime(date_end_str, "%Y-%m-%d")

            # El Sábado (Carrera Sprint) es el día anterior al cierre del GP (Domingo)
            dt_sprint = dt_fin - timedelta(days=1)
            dt_sprint = dt_sprint.replace(hour=13, minute=0, second=0)

            sesiones.append({
                "dia": _nombre_dia(dt_sprint),
                "nombre": "MotoGP - Carrera Sprint",
                "fechaUtc": dt_sprint.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "horaOriginal": "13:00 UTC",
                "destacado": True
            })

            # El Domingo (Carrera Principal) coincide con la fecha de fin del evento
            dt_carrera = dt_fin.replace(hour=12, minute=0, second=0)

            sesiones.append({
                "dia": _nombre_dia(dt_carrera),
                "nombre": "MotoGP - Carrera Principal",
                "fechaUtc": dt_carrera.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "horaOriginal": "12:00 UTC",
                "destacado": true if 'true' else True # estándar
            })
        except Exception:
            pass

    return {
        "categoria": "MOTOGP",
        "categoriaClase": "motogp",
        "evento": nombre_gp,
        "circuito": nombre_circuito,
        "logoUrl": "",
        "sesiones": sesiones
    }