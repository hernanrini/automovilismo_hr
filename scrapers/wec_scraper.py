# scrapers/wec_scraper.py

from datetime import datetime, timezone, timedelta

# Calendario oficial WEC de la temporada 2026
CALENDARIO_WEC_2026 = [
    {
        "evento": "1812 km of Qatar",
        "circuito": "Lusail International Circuit (Catar)",
        "inicio": "2026-02-27T08:00:00Z",
        "fin": "2026-02-28T16:00:00Z"
    },
    {
        "evento": "6 Hours of Imola",
        "circuito": "Autodromo Internazionale Enzo e Dino Ferrari (Italia)",
        "inicio": "2026-04-19T11:00:00Z",
        "fin": "2026-04-19T17:00:00Z"
    },
    {
        "evento": "6 Hours of Spa-Francorchamps",
        "circuito": "Circuit de Spa-Francorchamps (Bélgica)",
        "inicio": "2026-05-09T11:00:00Z",
        "fin": "2026-05-09T17:00:00Z"
    },
    {
        "evento": "24 Hours of Le Mans",
        "circuito": "Circuit de la Sarthe (Le Mans, Francia)",
        "inicio": "2026-06-13T14:00:00Z",
        "fin": "2026-06-14T14:00:00Z"
    },
    {
        "evento": "6 Hours of São Paulo",
        "circuito": "Autódromo José Carlos Pace - Interlagos (Brasil)",
        "inicio": "2026-07-12T14:00:00Z",
        "fin": "2026-07-12T20:00:00Z"
    },
    {
        "evento": "Lone Star Le Mans (COTA)",
        "circuito": "Circuit of the Americas (Austin, EE. UU.)",
        "inicio": "2026-09-06T18:00:00Z",
        "fin": "2026-09-07T00:00:00Z"
    },
    {
        "evento": "6 Hours of Fuji",
        "circuito": "Fuji Speedway (Japón)",
        "inicio": "2026-09-27T02:00:00Z",
        "fin": "2026-09-27T08:00:00Z"
    },
    {
        "evento": "8 Hours of Bahrain",
        "circuito": "Bahrain International Circuit (Sakhir, Baréin)",
        "inicio": "2026-11-07T11:00:00Z",
        "fin": "2026-11-07T19:00:00Z"
    }
]

def obtener_proximas_wec():
    """
    Filtra el calendario oficial del WEC para obtener las próximas citas
    y estructurar las sesiones clave de los fines de semana de resistencia.
    """
    try:
        ahora_utc = datetime.now(timezone.utc)
        proximos_eventos = []

        for cita in CALENDARIO_WEC_2026:
            dt_inicio = datetime.fromisoformat(cita["inicio"].replace('Z', '+00:00'))
            dt_fin = datetime.fromisoformat(cita["fin"].replace('Z', '+00:00'))

            # Si el evento ya terminó por completo, lo saltamos
            if dt_fin < ahora_utc:
                continue

            # Fechas y sesiones típicas de un fin de semana WEC
            dt_libre = dt_inicio - timedelta(days=2) # Entrenamientos libres (jueves/viernes previo)
            dt_quali = dt_inicio - timedelta(days=1) # Hyperpole / Clasificación
            dt_carrera = dt_inicio                  # Día principal de la prueba

            sesiones = [
                {
                    "dia": _formatear_dia(dt_libre),
                    "nombre": "Entrenamientos Libres",
                    "fechaUtc": dt_libre.strftime("%Y-%m-%dT10:00:00Z"),
                    "horaOriginal": "10:00 UTC",
                    "destacado": False
                },
                {
                    "dia": _formatear_dia(dt_quali),
                    "nombre": "Clasificación & Hyperpole",
                    "fechaUtc": dt_quali.strftime("%Y-%m-%dT13:00:00Z"),
                    "horaOriginal": "13:00 UTC",
                    "destacado": False
                },
                {
                    "dia": _formatear_dia(dt_carrera),
                    "nombre": f"Carrera ({cita['evento']})",
                    "fechaUtc": dt_carrera.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "horaOriginal": dt_carrera.strftime("%H:%M UTC"),
                    "destacado": True
                }
            ]

            proximos_eventos.append({
                "categoria": "WEC",
                "categoriaClase": "wec",
                "evento": cita["evento"],
                "circuito": cita["circuito"],
                "logoUrl": "",
                "sesiones": sesiones,
                "_dt_orden": dt_inicio
            })

        # Ordenar cronológicamente y limitar a los próximos 3 eventos
        proximos_eventos.sort(key=lambda x: x["_dt_orden"])
        
        for ev in proximos_eventos:
            ev.pop("_dt_orden", None)

        return proximos_eventos[:3]

    except Exception as e:
        print(f"⚠️ Error procesando WEC: {e}")
        return []

def _formatear_dia(dt):
    dias_semana = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
    return f"{dias_semana[dt.weekday()]} {dt.strftime('%d/%m')}"

if __name__ == "__main__":
    import json
    print(json.dumps(obtener_proximas_wec(), indent=4, ensure_ascii=False))