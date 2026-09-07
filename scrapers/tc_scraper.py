# scrapers/tc_scraper.py

from datetime import datetime, timezone, timedelta

# Calendario oficial Turismo Carretera y TC Pista de la temporada 2026
CALENDARIO_TC_2026 = [
    {
        "numero": 1,
        "circuito": "Autódromo Enrique 'Quique' Freile (El Calafate)",
        "inicio": "2026-02-14T09:00:00Z",
        "fin": "2026-02-15T17:00:00Z"
    },
    {
        "numero": 2,
        "circuito": "Autódromo Viedma (Río Negro)",
        "inicio": "2026-03-07T09:00:00Z",
        "fin": "2026-03-08T17:00:00Z"
    },
    {
        "numero": 3,
        "circuito": "Parque Provincia de Neuquén (Centenario)",
        "inicio": "2026-03-28T09:00:00Z",
        "fin": "2026-03-29T17:00:00Z"
    },
    {
        "numero": 4,
        "circuito": "Autódromo Oscar Cabalén (Alta Gracia, Córdoba)",
        "inicio": "2026-04-18T09:00:00Z",
        "fin": "2026-04-19T17:00:00Z"
    },
    {
        "numero": 5,
        "circuito": "Autódromo Termas de Río Hondo (Santiago del Estero)",
        "inicio": "2026-05-09T09:00:00Z",
        "fin": "2026-05-10T17:00:00Z"
    },
    {
        "numero": 6,
        "circuito": "Autódromo Ciudad de Rafaela (Santa Fe)",
        "inicio": "2026-05-30T09:00:00Z",
        "fin": "2026-05-31T17:00:00Z"
    },
    {
        "numero": 7,
        "circuito": "Autódromo Rosendo Hernández (San Luis)",
        "inicio": "2026-06-20T09:00:00Z",
        "fin": "2026-06-21T17:00:00Z"
    },
    {
        "numero": 8,
        "circuito": "Autódromo Rosamonte (Posadas, Misiones)",
        "inicio": "2026-07-11T09:00:00Z",
        "fin": "2026-07-12T17:00:00Z"
    },
    {
        "numero": 9,
        "circuito": "Autódromo San Juan Villicum (San Juan)",
        "inicio": "2026-08-01T09:00:00Z",
        "fin": "2026-08-02T17:00:00Z"
    },
    {
        "numero": 10,
        "circuito": "Autódromo Ciudad de Paraná (Entre Ríos)",
        "inicio": "2026-08-22T09:00:00Z",
        "fin": "2026-08-23T17:00:00Z"
    },
    {
        "numero": 11,
        "circuito": "Autódromo Rosendo Hernández - San Luis (Comienzo Copa de Oro)",
        "inicio": "2026-09-12T09:00:00Z",
        "fin": "2026-09-13T17:00:00Z"
    },
    {
        "numero": 12,
        "circuito": "Autódromo Ciudad de San Nicolás (Buenos Aires)",
        "inicio": "2026-10-03T09:00:00Z",
        "fin": "2026-10-04T17:00:00Z"
    },
    {
        "numero": 13,
        "circuito": "Autódromo de Rosario (Santa Fe)",
        "inicio": "2026-10-31T09:00:00Z",
        "fin": "2026-11-01T17:00:00Z"
    },
    {
        "numero": 14,
        "circuito": "Autódromo Parque Ciudad de Río Cuarto (Córdoba)",
        "inicio": "2026-11-28T09:00:00Z",
        "fin": "2026-11-29T17:00:00Z"
    }
]

def obtener_proximas_tc():
    """
    Filtra el calendario oficial para obtener las próximas citas de TC y TC Pista,
    nombrándolas como 'Turismo Carretera - Fecha #' y estructurando sus sesiones.
    """
    try:
        ahora_utc = datetime.now(timezone.utc)
        proximos_eventos = []

        for cita in CALENDARIO_TC_2026:
            dt_inicio = datetime.fromisoformat(cita["inicio"].replace('Z', '+00:00'))
            dt_fin = datetime.fromisoformat(cita["fin"].replace('Z', '+00:00'))

            if dt_fin < ahora_utc:
                continue

            dt_sabado = dt_inicio
            dt_domingo = dt_fin
            nombre_evento = f"Turismo Carretera - Fecha {cita['numero']}"

            sesiones = [
                {
                    "dia": _formatear_dia(dt_sabado),
                    "nombre": "TC Pista - Clasificación",
                    "fechaUtc": dt_sabado.strftime("%Y-%m-%dT11:00:00Z"),
                    "horaOriginal": "11:00 UTC",
                    "destacado": False
                },
                {
                    "dia": _formatear_dia(dt_sabado),
                    "nombre": "TC - Entrenamientos & Clasificación",
                    "fechaUtc": dt_sabado.strftime("%Y-%m-%dT13:00:00Z"),
                    "horaOriginal": "13:00 UTC",
                    "destacado": False
                },
                {
                    "dia": _formatear_dia(dt_domingo),
                    "nombre": "TC Pista - Series / Final",
                    "fechaUtc": dt_domingo.strftime("%Y-%m-%dT11:00:00Z"),
                    "horaOriginal": "11:00 UTC",
                    "destacado": False
                },
                {
                    "dia": _formatear_dia(dt_domingo),
                    "nombre": "TC - Series Clasificatorias",
                    "fechaUtc": dt_domingo.strftime("%Y-%m-%dT13:00:00Z"),
                    "horaOriginal": "13:00 UTC",
                    "destacado": False
                },
                {
                    "dia": _formatear_dia(dt_domingo),
                    "nombre": f"{nombre_evento} - Final",
                    "fechaUtc": dt_domingo.strftime("%Y-%m-%dT17:00:00Z"),
                    "horaOriginal": "17:00 UTC",
                    "destacado": True
                }
            ]

            proximos_eventos.append({
                "categoria": "Turismo Carretera & TC Pista",
                "categoriaClase": "tc",
                "evento": nombre_evento,
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
        print(f"⚠️ Error procesando TC y TC Pista: {e}")
        return []

def _formatear_dia(dt):
    dias_semana = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
    return f"{dias_semana[dt.weekday()]} {dt.strftime('%d/%m')}"

if __name__ == "__main__":
    import json
    print(json.dumps(obtener_proximas_tc(), indent=4, ensure_ascii=False))