# scrapers/wrc_scraper.py

from datetime import datetime, timezone, timedelta

# Calendario oficial WRC de la temporada 2026
CALENDARIO_WRC_2026 = [
    {
        "evento": "Rallye Monte-Carlo",
        "circuito": "Monte Carlo (Mónaco)",
        "inicio": "2026-01-22T08:00:00Z",
        "fin": "2026-01-25T16:00:00Z"
    },
    {
        "evento": "Rally Sweden",
        "circuito": "Umeå (Suecia)",
        "inicio": "2026-02-12T08:00:00Z",
        "fin": "2026-02-15T16:00:00Z"
    },
    {
        "evento": "Safari Rally Kenya",
        "circuito": "Naivasha (Kenia)",
        "inicio": "2026-03-12T08:00:00Z",
        "fin": "2026-03-15T16:00:00Z"
    },
    {
        "evento": "Croatia Rally",
        "circuito": "Zagreb (Croacia)",
        "inicio": "2026-04-09T08:00:00Z",
        "fin": "2026-04-12T16:00:00Z"
    },
    {
        "evento": "Rally Islas Canarias",
        "circuito": "Las Palmas (España)",
        "inicio": "2026-04-23T08:00:00Z",
        "fin": "2026-04-26T16:00:00Z"
    },
    {
        "evento": "Rally de Portugal",
        "circuito": "Matosinhos (Portugal)",
        "inicio": "2026-05-07T08:00:00Z",
        "fin": "2026-05-10T16:00:00Z"
    },
    {
        "evento": "Rally Japan",
        "circuito": "Toyota (Japón)",
        "inicio": "2026-05-28T08:00:00Z",
        "fin": "2026-05-31T16:00:00Z"
    },
    {
        "evento": "Acropolis Rally Greece",
        "circuito": "Lamia (Grecia)",
        "inicio": "2026-06-25T08:00:00Z",
        "fin": "2026-06-28T16:00:00Z"
    },
    {
        "evento": "Rally Estonia",
        "circuito": "Tartu (Estonia)",
        "inicio": "2026-07-16T08:00:00Z",
        "fin": "2026-07-19T16:00:00Z"
    },
    {
        "evento": "Rally Finland",
        "circuito": "Jyväskylä (Finlandia)",
        "inicio": "2026-07-30T08:00:00Z",
        "fin": "2026-08-02T16:00:00Z"
    },
    {
        "evento": "Rally del Paraguay",
        "circuito": "Encarnación (Paraguay)",
        "inicio": "2026-08-27T08:00:00Z",
        "fin": "2026-08-30T16:00:00Z"
    },
    {
        "evento": "Rally Chile Bio Bío",
        "circuito": "Biobío (Chile)",
        "inicio": "2026-09-10T08:00:00Z",
        "fin": "2026-09-13T16:00:00Z"
    },
    {
        "evento": "Rally Italia Sardegna",
        "circuito": "Cerdeña (Italia)",
        "inicio": "2026-10-01T08:00:00Z",
        "fin": "2026-10-04T16:00:00Z"
    },
    {
        "evento": "Rally Saudi Arabia",
        "circuito": "Arabia Saudí",
        "inicio": "2026-11-11T08:00:00Z",
        "fin": "2026-11-14T16:00:00Z"
    }
]

def obtener_proximas_wrc():
    """
    Filtra el calendario oficial del WRC para obtener las próximas citas
    de los próximos fines de semana estructurando sus sesiones clave.
    """
    try:
        ahora_utc = datetime.now(timezone.utc)
        proximos_eventos = []

        for rally in CALENDARIO_WRC_2026:
            dt_inicio = datetime.fromisoformat(rally["inicio"].replace('Z', '+00:00'))
            dt_fin = datetime.fromisoformat(rally["fin"].replace('Z', '+00:00'))

            # Si el rally ya terminó por completo, lo saltamos
            if dt_fin < ahora_utc:
                continue

            dt_shakedown = dt_inicio
            dt_etapas = dt_inicio + timedelta(days=2)
            dt_power = dt_fin

            sesiones = [
                {
                    "dia": _formatear_dia(dt_shakedown),
                    "nombre": "Shakedown",
                    "fechaUtc": dt_shakedown.strftime("%Y-%m-%dT08:00:00Z"),
                    "horaOriginal": "08:00 UTC",
                    "destacado": False
                },
                {
                    "dia": _formatear_dia(dt_etapas),
                    "nombre": "Etapa - Tramos Especiales",
                    "fechaUtc": dt_etapas.strftime("%Y-%m-%dT07:00:00Z"),
                    "horaOriginal": "07:00 UTC",
                    "destacado": False
                },
                {
                    "dia": _formatear_dia(dt_power),
                    "nombre": "Wolf Power Stage Final",
                    "fechaUtc": dt_power.strftime("%Y-%m-%dT10:15:00Z"),
                    "horaOriginal": "10:15 UTC",
                    "destacado": True
                }
            ]

            proximos_eventos.append({
                "categoria": "WRC",
                "categoriaClase": "wrc",
                "evento": rally["evento"],
                "circuito": rally["circuito"],
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
        print(f"⚠️ Error procesando WRC: {e}")
        return []

def _formatear_dia(dt):
    dias_semana = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
    return f"{dias_semana[dt.weekday()]} {dt.strftime('%d/%m')}"