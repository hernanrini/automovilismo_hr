import json
import traceback
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

from scrapers.f1_scraper import obtener_proximas_f1
from scrapers.indy_scraper import obtener_proximas_indy
from scrapers.wrc_scraper import obtener_proximas_wrc
from scrapers.nascar_scraper import obtener_proximas_nascar
from scrapers.tc_scraper import obtener_proximas_tc
from scrapers.wec_scraper import obtener_proximas_wec
from scrapers.motogp_scraper import obtener_proximas_motogp

print("🤖 Compilando calendario dinámico completo (todo el año)...")

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

    if idx == 1:
        estado_semana = "FIN DE SEMANA ACTUAL"
    elif idx == 2:
        estado_semana = "PRÓXIMO FIN DE SEMANA"
    else:
        estado_semana = "FUTURO"

    eventos_en_esta_semana = [item["evento_obj"] for item in items]

    datos_agenda.append({
        "semana": idx,
        "tituloSemana": titulo_semana,
        "estado": estado_semana,
        "eventos": eventos_en_esta_semana
    })

with open("carreras.json", "w", encoding="utf-8") as f:
    json.dump(datos_agenda, f, ensure_ascii=False, indent=2)

print("✅ `carreras.json` actualizado.")

try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Restauracion de calendario base"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("🎉 Sincronizado con GitHub.")
except Exception as e:
    print(f"⚠️ Git omitido: {e}")