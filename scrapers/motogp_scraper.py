import requests
from datetime import datetime

def obtener_proximas_motogp():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    eventos_motogp = []
    
    try:
        # 1. Obtenemos las temporadas para sacar el ID de la temporada actual
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

        # 2. Obtenemos los eventos (GG.PP.) de esa temporada sin filtrar fechas
        url_events = f"https://api.motogp.pulselive.com/motogp/v1/results/events?seasonUuid={season_id}"
        res_events = requests.get(url_events, headers=headers, timeout=10)
        res_events.raise_for_status()
        events = res_events.json()
        print(f"MotoGP API: Se encontraron {len(events)} eventos en total.")

        for ev in events:
            evento_formateado = _formatear_evento_motogp(ev, headers)
            if evento_formateado:
                eventos_motogp.append(evento_formateado)

        print(f"MotoGP API: {len(eventos_motogp)} eventos procesados correctamente.")
        return eventos_motogp
    except Exception as e:
        print(f"⚠️ Error scraping MotoGP: {e}")
        return eventos_motogp

def _nombre_dia(dt):
    dias = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
    return f"{dias[dt.weekday()]} {dt.day:02d}/{dt.month:02d}"

def _formatear_evento_motogp(ev, headers):
    nombre_gp = ev.get("name", "Gran Premio de MotoGP")
    circuito_info = ev.get("circuit", {})
    nombre_circuito = circuito_info.get("name", "Circuito MotoGP")
    
    event_uuid = ev.get("id")
    sesiones = []

    if event_uuid:
        try:
            url_sessions = f"https://api.motogp.pulselive.com/motogp/v1/results/sessions?eventUuid={event_uuid}"
            res_ses = requests.get(url_sessions, headers=headers, timeout=10)
            if res_ses.status_code == 200:
                sessions_data = res_ses.json()
                for ses in sessions_data:
                    ses_name = ses.get("type", "Sesión")
                    date_str = ses.get("date") or ses.get("dateStart")
                    
                    if date_str:
                        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        utc_str = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                        
                        es_carrera = "RACE" in ses_name.upper() or "GP" in ses_name.upper()
                        es_sprint = "SPRINT" in ses_name.upper()
                        destacado = es_carrera or es_sprint
                        
                        nombre_limpio = f"MotoGP - {ses_name.replace('_', ' ').title()}"
                        if es_carrera and "SPRINT" not in ses_name.upper():
                            nombre_limpio = "MotoGP - Carrera Principal"
                        elif es_sprint:
                            nombre_limpio = "MotoGP - Carrera Sprint"

                        sesiones.append({
                            "dia": _nombre_dia(dt),
                            "nombre": nombre_limpio,
                            "fechaUtc": utc_str,
                            "horaOriginal": f"{dt.strftime('%H:%M')} UTC",
                            "destacado": destacado
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