# scrapers/nascar_scraper.py

from datetime import datetime, timezone, timedelta
from pynascar import Schedule

def _a_utc(val):
    """Convierte cualquier fecha a datetime con zona horaria UTC."""
    if val is None:
        return None
    if isinstance(val, str):
        dt = datetime.fromisoformat(val.replace('Z', '+00:00'))
    else:
        dt = val
    
    if hasattr(dt, 'tzinfo') and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    elif hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
        return dt.astimezone(timezone.utc)
    return dt

def obtener_proximas_nascar():
    """
    Obtiene las próximas citas de la NASCAR (Cup, Xfinity y Craftsman Trucks) 
    unificando el etiquetado de las series y usando UTC puro como referencia horaria.
    """
    try:
        series_info = {
            1: {"nombre_base": "NASCAR CUP SERIES", "etiqueta": "NASCAR Cup Series", "prioridad_evento": 1},
            2: {"nombre_base": "NASCAR XFINITY SERIES", "etiqueta": "NASCAR Xfinity Series", "prioridad_evento": 2},
            3: {"nombre_base": "NASCAR TRUCK SERIES", "etiqueta": "NASCAR Craftsman Truck Series", "prioridad_evento": 3}
        }

        eventos_agrupados = {}
        ahora_utc = datetime.now(timezone.utc)

        for series_id, info in series_info.items():
            schedule = Schedule(2026, series_id)
            proximas = schedule.get_remaining_races()

            for _, fila in proximas.iterrows():
                track_name = fila.get("track_name", "Desconocido")
                race_name = fila.get("race_name", "Carrera NASCAR")
                race_date_raw = fila.get("date_scheduled")
                
                if not race_date_raw:
                    continue

                fecha_dt = _a_utc(race_date_raw)
                if fecha_dt < ahora_utc:
                    continue

                lunes_semana = fecha_dt - timedelta(days=fecha_dt.weekday())
                clave_fin_de_semana = (track_name.strip().lower(), lunes_semana.strftime("%Y-%m-%d"))

                if clave_fin_de_semana not in eventos_agrupados:
                    eventos_agrupados[clave_fin_de_semana] = {
                        "categoria": "NASCAR CUP SERIES",
                        "categoriaClase": "nascar",
                        "evento": race_name,
                        "prioridad_evento": info["prioridad_evento"],
                        "circuito": f"{track_name} (EE.UU.)",
                        "logoUrl": "",
                        "sesiones_raw": []
                    }
                else:
                    if info["prioridad_evento"] < eventos_agrupados[clave_fin_de_semana]["prioridad_evento"]:
                        eventos_agrupados[clave_fin_de_semana]["evento"] = race_name
                        eventos_agrupados[clave_fin_de_semana]["prioridad_evento"] = info["prioridad_evento"]

                agenda_eventos = fila.get("schedule", [])
                sesion_carrera_agregada = False

                for item in agenda_eventos:
                    evento_nombre = item.get("event_name", "")
                    start_time_raw = item.get("start_time_utc", "")

                    if not start_time_raw:
                        continue

                    dt_sesion = _a_utc(start_time_raw)
                    if dt_sesion < ahora_utc:
                        continue

                    dia_str = _formatear_dia(dt_sesion)
                    fecha_utc_iso = dt_sesion.strftime("%Y-%m-%dT%H:%M:%SZ")
                    hora_utc_str = dt_sesion.strftime("%H:%M UTC")

                    is_cup = (series_id == 1)

                    if "Qualifying" in evento_nombre:
                        eventos_agrupados[clave_fin_de_semana]["sesiones_raw"].append({
                            "dt": dt_sesion,
                            "sesion": {
                                "dia": dia_str,
                                "nombre": f"{info['etiqueta']} - Clasificación",
                                "fechaUtc": fecha_utc_iso,
                                "horaOriginal": hora_utc_str,
                                "destacado": is_cup
                            }
                        })
                    elif "Race" in evento_nombre:
                        sufijo_extra = f" - Principal ({race_name})" if is_cup else f" ({race_name})"
                        eventos_agrupados[clave_fin_de_semana]["sesiones_raw"].append({
                            "dt": dt_sesion,
                            "sesion": {
                                "dia": dia_str,
                                "nombre": f"{info['etiqueta']} - Carrera{sufijo_extra}",
                                "fechaUtc": fecha_utc_iso,
                                "horaOriginal": hora_utc_str,
                                "destacado": is_cup
                            }
                        })
                        sesion_carrera_agregada = True

                if not sesion_carrera_agregada and fecha_dt >= ahora_utc:
                    dia_str = _formatear_dia(fecha_dt)
                    is_cup = (series_id == 1)
                    eventos_agrupados[clave_fin_de_semana]["sesiones_raw"].append({
                        "dt": fecha_dt,
                        "sesion": {
                            "dia": dia_str,
                            "nombre": f"{info['etiqueta']} - Carrera",
                            "fechaUtc": fecha_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "horaOriginal": fecha_dt.strftime("%H:%M UTC"),
                            "destacado": is_cup
                        }
                    })

        resultado_final = []
        for clave, datos in eventos_agrupados.items():
            if not datos["sesiones_raw"]:
                continue

            vistos = set()
            sesiones_unicas = []
            for s in datos["sesiones_raw"]:
                identificador = (s["sesion"]["fechaUtc"], s["sesion"]["nombre"])
                if identificador not in vistos:
                    vistos.add(identificador)
                    sesiones_unicas.append(s)

            sesiones_unicas.sort(key=lambda x: x["dt"])
            sesiones_limpias = [s["sesion"] for s in sesiones_unicas]
            
            resultado_final.append({
                "categoria": datos["categoria"],
                "categoriaClase": datos["categoriaClase"],
                "evento": datos["evento"],
                "circuito": datos["circuito"],
                "logoUrl": datos["logoUrl"],
                "sesiones": sesiones_limpias
            })

        resultado_final.sort(key=lambda x: x["sesiones"][0]["fechaUtc"] if x["sesiones"] else "")
        return resultado_final[:3]

    except Exception as e:
        print(f"⚠️ Error scraping NASCAR con pynascar: {e}")
        return []

def _formatear_dia(dt):
    """Convierte un datetime en el formato de texto ej: 'SÁBADO 05/09'"""
    dias_semana = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
    nombre_dia = dias_semana[dt.weekday()]
    return f"{nombre_dia} {dt.strftime('%d/%m')}"

if __name__ == "__main__":
    import json
    citas = obtener_proximas_nascar()
    print(json.dumps(citas, indent=4, ensure_ascii=False))