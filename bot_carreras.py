import json
import traceback
import subprocess
from datetime import datetime
from collections import defaultdict

from scrapers.f1_scraper import obtener_proximas_f1
from scrapers.indy_scraper import obtener_proximas_indy
from scrapers.wrc_scraper import obtener_proximas_wrc
from scrapers.nascar_scraper import obtener_proximas_nascar
from scrapers.tc_scraper import obtener_proximas_tc
from scrapers.wec_scraper import obtener_proximas_wec
from scrapers.motogp_scraper import obtener_proximas_motogp

print("🤖 Compilando calendario dinámico...")

eventos_totales = []
scrapers = [
    obtener_proximas_f1,
    obtener_proximas_indy,
    obtener_proximas_wrc,
    obtener_proximas_nascar,
    obtener_proximas_tc,
    obtener_proximas_wec,
    obtener_proximas_motogp,
]

for scraper in scrapers:
    try:
        res = scraper()
        if isinstance(res, list):
            eventos_totales.extend(res)
        elif isinstance(res, dict):
            eventos_totales.append(res)
    except Exception as e:
        print(f"⚠️ Error en scraper {scraper.__name__}: {e}")
        traceback.print_exc()

print(f"📊 Total de eventos brutos obtenidos: {len(eventos_totales)}")

calendario_agrupado = defaultdict(list)

for evento in eventos_totales:
    try:
        if not evento.get("sesiones"):
            continue

        sesiones_validas = [s for s in evento["sesiones"] if s.get("fechaUtc")]
        if not sesiones_validas:
            continue

        sesiones_validas.sort(key=lambda s: s["fechaUtc"])
        evento["sesiones"] = sesiones_validas

        fechas_sesiones = [s["fechaUtc"].split("T")[0] for s in sesiones_validas]
        max_fecha = max(fechas_sesiones)
        dt_fin = datetime.strptime(max_fecha, "%Y-%m-%d")

        clave_orden = dt_fin.strftime("%Y-%W")

        calendario_agrupado[clave_orden].append({
            "evento_obj": evento,
            "fecha_comparacion": dt_fin
        })
    except Exception as e:
        print(f"⚠️ Error procesando evento {evento.get('nombre', '???')}: {e}")

claves_ordenadas = sorted(calendario_agrupado.keys())

datos_agenda = []
for idx, clave in enumerate(claves_ordenadas, start=1):
    items = calendario_agrupado[clave]
    fechas_grupo = [item["fecha_comparacion"] for item in items]
    fecha_principal = max(fechas_grupo)
    titulo_semana = f"Fin de semana {fecha_principal.strftime('%d/%m')}"

    eventos_en_esta_semana = [item["evento_obj"] for item in items]

    datos_agenda.append({
        "semana": idx,
        "tituloSemana": titulo_semana,
        "estado": "FUTURO",
        "eventos": eventos_en_esta_semana
    })

# --- FILTRAR SEMANAS PASADAS DE FORMA SEGURA ---
hoy_str = datetime.now().strftime("%Y-%m-%d")
print(f"📅 Fecha actual de referencia: {hoy_str}")

datos_agenda_filtrados = []
for semana in datos_agenda:
    semana_vigente = False
    for evento in semana["eventos"]:
        for sesion in evento.get("sesiones", []):
            fecha_sesion = sesion.get("fechaUtc", "").split("T")[0]
            if fecha_sesion >= hoy_str:
                semana_vigente = True
                break
        if semana_vigente:
            break
            
    if semana_vigente:
        datos_agenda_filtrados.append(semana)

print(f"📦 Semanas después del filtro: {len(datos_agenda_filtrados)} de {len(datos_agenda)}")

# Si por lo que sea el filtro deja todo a 0, recuperamos la agenda completa para que la web no se quede vacía
if len(datos_agenda_filtrados) == 0:
    print("⚠️ El filtro dejó la agenda vacía. Usando la agenda completa sin filtrar como seguridad.")
    datos_agenda_filtrados = datos_agenda

# Reasignar índices y estados
for idx, semana_data in enumerate(datos_agenda_filtrados, start=1):
    semana_data["semana"] = idx
    if idx == 1:
        semana_data["estado"] = "FIN DE SEMANA ACTUAL"
    elif idx == 2:
        semana_data["estado"] = "PRÓXIMO FIN DE SEMANA"
    else:
        semana_data["estado"] = "FUTURO"

with open("carreras.json", "w", encoding="utf-8") as f:
    json.dump(datos_agenda_filtrados, f, ensure_ascii=False, indent=2)

print("✅ `carreras.json` guardado correctamente.")

# --- GIT SEGURO ---
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Actualizar calendario de carreras"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("🎉 Sincronizado con GitHub con éxito.")
except Exception as e:
    print(f"⚠️ Git omitido o sin cambios pendientes: {e}")