# diagnostico_nascar.py
# Este script NO es el scraper final — solo sirve para inspeccionar
# qué datos trae realmente pynascar antes de construir nascar_scraper.py

from pynascar import Schedule

# Series: 1=Cup, 2=Xfinity, 3=Trucks
series_nombres = {1: "CUP", 2: "XFINITY", 3: "TRUCK"}

for series_id, nombre in series_nombres.items():
    print(f"\n{'='*60}")
    print(f"SERIE: {nombre} (series_id={series_id})")
    print('='*60)
    
    try:
        schedule = Schedule(2026, series_id)
        
        print(f"\nColumnas disponibles: {list(schedule.data.columns)}")
        
        proximas = schedule.get_remaining_races()
        print(f"\nCarreras restantes en 2026: {len(proximas)}")
        
        # Mostramos las 3 próximas con TODOS sus datos, sin recortar
        print("\nPrimeras 3 carreras próximas (todos los campos):")
        for i, fila in proximas.head(3).iterrows():
            print(f"\n--- Carrera {i} ---")
            for campo, valor in fila.items():
                print(f"  {campo}: {valor}")
                
    except Exception as e:
        print(f"⚠️ Error con la serie {nombre}: {e}")

print(f"\n{'='*60}")
print("Diagnóstico completo. Copia toda esta salida y compártela.")
print('='*60)