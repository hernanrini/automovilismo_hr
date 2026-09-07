# scrapers/indy_scraper.py

from datetime import datetime, timezone, timedelta

# Calendario oficial NTT INDYCAR SERIES (y Indy NXT) de la temporada 2026
CALENDARIO_INDY_2026 = [
    {
        "evento": "Grand Prix of St. Petersburg",
        "circuito": "Streets of St. Petersburg (Florida, EE. UU.)",
        "inicio": "2026-03-01T17:00:00Z",
        "fin": "2026-03-01T20:00:00Z"
    },
    {
        "evento": "$1 Million Challenge (The Thermal Club)",
        "circuito": "The Thermal Club (California, EE. UU.)",
        "inicio": "2026-03-22T17:00:00Z",
        "fin": "2026-03-22T20:00:00Z"
    },
    {
        "evento": "Acura Grand Prix of Long Beach",
        "circuito": "Streets of Long Beach (California, EE. UU.)",
        "inicio": "2026-04-12T19:00:00Z",
        "fin": "2026-04-12T22:00:00Z"
    },
    {
        "evento": "Children's of Alabama Indy Grand Prix",
        "circuito": "Barber Motorsports Park (Alabama, EE. UU.)",
        "inicio": "2026-04-26T17:00:00Z",
        "fin": "2026-04-26T20:00:00Z"
    },
    {
        "evento": "Sonsio Grand Prix (Indy Road Course)",
        "circuito": "Indianapolis Motor Speedway - Road Course (Indiana)",
        "inicio": "2026-05-09T19:00:00Z",
        "fin": "2026-05-09T22:00:00Z"
    },
    {
        "evento": "110th Running of the Indianapolis 500",
        "circuito": "Indianapolis Motor Speedway - Oval (Indiana)",
        "inicio": "2026-05-24T16:00:00Z",
        "fin": "2026-05-24T21:00:00Z"
    },
    {
        "evento": "Chevrolet Detroit Grand Prix",
        "circuito": "Streets of Detroit (Míchigan, EE. UU.)",
        "inicio": "2026-05-31T19:00:00Z",
        "fin": "2026-05-31T22:00:00Z"
    },
    {
        "evento": "Bommarito Automotive Group 500",
        "circuito": "World Wide Technology Raceway (Gateway, Illinois)",
        "inicio": "2026-06-07T19:00:00Z",
        "fin": "2026-06-07T22:00:00Z"
    },
    {
        "evento": "Road America Grand Prix",
        "circuito": "Road America (Elkhart Lake, Wisconsin)",
        "inicio": "2026-06-21T18:00:00Z",
        "fin": "2026-06-21T21:00:00Z"
    },
    {
        "evento": "Mid-Ohio Sports Car Course",
        "circuito": "Mid-Ohio Sports Car Course (Lexington, Ohio)",
        "inicio": "2026-07-05T17:00:00Z",
        "fin": "2026-07-05T20:00:00Z"
    },
    {
        "evento": "Iowa IndyCar 250s (Race 1 & 2)",
        "circuito": "Iowa Speedway (Newton, Iowa)",
        "inicio": "2026-07-18T18:00:00Z",
        "fin": "2026-07-19T21:00:00Z"
    },
    {
        "evento": "Honda Indy Toronto",
        "circuito": "Exhibition Place (Toronto, Canadá)",
        "inicio": "2026-07-26T18:00:00Z",
        "fin": "2026-07-26T21:00:00Z"
    },
    {
        "evento": "Bommarito Automotive Group 500 (Vuelta / Oregón u otro)",
        "circuito": "Portland International Raceway (Oregón)",
        "inicio": "2026-08-09T19:00:00Z",
        "fin": "2026-08-09T22:00:00Z"
    },
    {
        "evento": "Milwaukee Mile Grand Prix",
        "circuito": "Milwaukee Mile (West Allis, Wisconsin)",
        "inicio": "2026-08-23T18:00:00Z",
        "fin": "2026-08-23T21:00:00Z"
    },
    {
        "evento": "Big Machine Music City Grand Prix (Final)",
        "circuito": "Nashville Superspeedway (Tennessee)",
        "inicio": "2026-09-06T19:00:00Z",
        "fin": "2026-09-06T22:00:00Z"
    }
]

def obtener_proximas_indy():
    """
    Filtra el calendario oficial para obtener las próximas citas de IndyCar y Indy NXT,
    estructurando sus sesiones cronológicamente.
    """
    try:
        ahora_utc = datetime.now(timezone.utc)
        proximos_eventos = []

        for cita in CALENDARIO_INDY_2026:
            dt_inicio = datetime.fromisoformat(cita["inicio"].replace('Z', '+00:00'))
            dt_fin = datetime.fromisoformat(cita["fin"].replace('Z', '+00:00'))

            if dt_fin < ahora_utc:
                continue

            dt_sabado = dt_inicio - timedelta(days=1)
            dt_domingo = dt_inicio

            sesiones = [
                {
                    "dia": _formatear_dia(dt_sabado),
                    "nombre": "Indy NXT - Entrenamientos y Clasificación",
                    "fechaUtc": dt_sabado.strftime("%Y-%m-%dT18:00:00Z"),
                    "horaOriginal": "18:00 UTC",
                    "destacado": False
                },
                {
                    "dia": _formatear_dia(dt_sabado),
                    "nombre": "IndyCar - Clasificación / Fast Six",
                    "fechaUtc": dt_sabado.strftime("%Y-%m-%dT20:00:00Z"),
                    "horaOriginal": "20:00 UTC",
                    "destacado": False
                },
                {
                    "dia": _formatear_dia(dt_domingo),
                    "nombre": "Indy NXT - Carrera",
                    "fechaUtc": dt_domingo.strftime("%Y-%m-%dT16:00:00Z"),
                    "horaOriginal": "16:00 UTC",
                    "destacado": False
                },
                {
                    "dia": _formatear_dia(dt_domingo),
                    "nombre": f"IndyCar - Carrera ({cita['evento']})",
                    "fechaUtc": dt_domingo.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "horaOriginal": dt_domingo.strftime("%H:%M UTC"),
                    "destacado": True
                }
            ]

            proximos_eventos.append({
                "categoria": "IndyCar & Indy NXT",
                "categoriaClase": "indy",
                "evento": cita["evento"],
                "circuito": cita["circuito"],
                "logoUrl": "",
                "sesiones": sesiones,
                "_dt_orden": dt_inicio
            })

        proximos_eventos.sort(key=lambda x: x["_dt_orden"])
        
        for ev in proximos_eventos:
            ev.pop("_dt_orden", None)

        return proximos_eventos[:3]

    except Exception as e:
        print(f"⚠️ Error procesando IndyCar: {e}")
        return []

def _formatear_dia(dt):
    dias_semana = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
    return f"{dias_semana[dt.weekday()]} {dt.strftime('%d/%m')}"

if __name__ == "__main__":
    import json
    print(json.dumps(obtener_proximas_indy(), indent=4, ensure_ascii=False))