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

        # 2. Obtenemos los eventos (GG.PP.) de esa temporada
        url_events = f"https://api.motogp.pulselive.com/motogp/v1/results/events?seasonUuid={season_id}"
        res_events = requests.get(url_events, headers=headers, timeout=10)
        res_events.raise_for_status()
        events = res_events.json()
        print(f"MotoGP API: Se encontraron {len(events)} eventos en total.")

        for ev in events:
            evento_formateado = _formatear_evento_motogp(ev, headers)
            if evento_formateado and evento_formateado.get("sesiones"):
                eventos_motogp.append(evento_formateado)

        print(f"MotoGP API: {len(eventos_motogp)} eventos procesados correctamente con sesiones.")
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
                    # Buscamos el tipo o nombre en varias claves posibles de la API
                    ses_type = ses.get("type") or ""
                    ses_title = ses.get("name") or ses.get("sessionTitle") or ses_type
                    ses_name_upper = f"{ses_type} {ses_title}".upper()
                    
                    date_str = ses.get("date") or ses.get("dateStart")
                    
                    if date_str:
                        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        utc_str = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                        
                        es_carrera = "RACE" in ses_name_upper or "GP" in ses_name_upper or "RAC" in ses_name_upper
                        es_sprint = "SPRINT" in ses_name_upper
                        destacado = es_carrera or es_sprint
                        
                        # Limpieza del nombre de la sesión para que luzca bien en la web
                        if es_carrera and "SPRINT" not in ses_name_upper:
                            nombre_limpio = "MotoGP - Carrera Principal"
                        elif es_sprint:
                            nombre_limpio = "MotoGP - Carrera Sprint"
                        elif "P" in ses_type.upper() or "PRACTICE" in ses_name_upper:
                            nombre_limpio = f"MotoGP - Prácticas {ses_type}"
                        elif "Q" in ses_type.upper() or "QUALIFYING" in ses_name_upper:
                            nombre_limpio = f"MotoGP - Clasificación {ses_type}"
                        else:
                            nombre_limpio = f"MotoGP - {ses_title.title()}"

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