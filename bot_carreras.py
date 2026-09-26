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

        # Descartamos sesiones sin fechaUtc en vez de romper el sort
        sesiones_validas = [s for s in evento["sesiones"] if s.get("fechaUtc")]
        if not sesiones_validas:
            print(f"⚠️ Evento sin sesiones con fechaUtc válida, se descarta: {evento.get('nombre', '???')}")
            continue

        # Ordenar sesiones cronológicamente por UTC
        sesiones_validas.sort(key=lambda s: s["fechaUtc"])
        evento["sesiones"] = sesiones_validas

        # Tomamos la fecha de la sesión principal para definir el fin de semana
        fechas_sesiones = [s["fechaUtc"].split("T")[0] for s in sesiones_validas]
        max_fecha = max(fechas_sesiones)
        dt_fin = datetime.strptime(max_fecha, "%Y-%m-%d")

        # Agrupar por año y semana del año (ej. 2026-36)
        clave_orden = dt_fin.strftime("%Y-%W")

        calendario_agrupado[clave_orden].append({
            "evento_obj": evento,
            "fecha_comparacion": dt_fin
        })
    except Exception as e:
        print(f"⚠️ Error procesando evento {evento.get('nombre', '???')}: {e}")
        traceback.print_exc()

# Ordenar TODAS las semanas cronológicamente
claves_ordenadas = sorted(calendario_agrupado.keys())

datos_agenda = []
for idx_orig, clave in enumerate(claves_ordenadas, start=1):
    items = calendario_agrupado[clave]

    # Buscamos la fecha máxima de ese grupo para sacar el domingo de carreras
    fechas_grupo = [item["fecha_comparacion"] for item in items]
    fecha_principal = max(fechas_grupo)

    # Formato solicitado: "Fin de semana DD/MM"
    titulo_semana = f"Fin de semana {fecha_principal.strftime('%d/%m')}"

    eventos_en_esta_semana = [item["evento_obj"] for item in items]

    datos_agenda.append({
        "semana": idx_orig,
        "tituloSemana": titulo_semana,
        "estado": "FUTURO",
        "eventos": eventos_en_esta_semana,
        "fecha_maxima": fecha_principal # Campo auxiliar para filtrar
    })

# --- FILTRAR PARA DESCARTAR SEMANAS PASADAS ---
hoy_str = datetime.now().strftime("%Y-%m-%d")
datos_agenda_filtrados = []

for semana in datos_agenda:
    # Comprobamos si el fin de semana es hoy o futuro
    semana_vigente = False
    for evento in semana["eventos"]:
        for sesion in evento.get("sesiones", []):
            if sesion.get("fechaUtc", "").split("T")[0] >= hoy_str:
                semana_vigente = True
                break
        if semana_vigente:
            break
            
    if semana_vigente:
        # Eliminamos la clave auxiliar antes de guardar
        semana.pop("fecha_maxima", None)
        datos_agenda_filtrados.append(semana)

# Reasignar índices y estados para que la primera semana visible sea la actual
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

print("✅ `carreras.json` actualizado con éxito (se semanas pasadas filtradas).")

# --- BLOQUE PARA SUBIR AUTOMÁTICAMENTE EL CAMBIO A GITHUB ---
try:
    print("🚀 Subiendo cambios a GitHub...")
    subprocess.run(["git", "config", "--global", "user.name", "Rino Dev Bot"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "bot@automovilismohr.com"], check=True)
    
    # Añadimos TODOS los archivos modificados
    subprocess.run(["git", "add", "."], check=True)
    
    # Hacemos el commit
    subprocess.run(["git", "commit", "-m", "Calendario limpio y actualizado automáticamente"], check=True)
    
    # Hacemos push a la rama principal (main)
    subprocess.run(["git", "push"], check=True)
    print("🎉 ¡Cambios subidos a GitHub con éxito! Vercel desplegará automáticamente.")
except Exception as e:
    print(f"⚠️ No se pudo hacer el commit automático: {e}")