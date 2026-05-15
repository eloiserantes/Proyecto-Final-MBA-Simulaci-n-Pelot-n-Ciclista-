import gpxpy
import pandas as pd

def convertir_gpx_a_csv(archivo_gpx, archivo_csv, intervalo_m=100):
    """
    Lee un archivo GPX y genera un CSV con la inclinación cada X metros.
    """
    print(f"Leyendo archivo {archivo_gpx}...")
    
    with open(archivo_gpx, 'r', encoding='utf-8') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    datos = []
    distancia_acumulada = 0.0
    punto_anterior = None
    
    # Variables para suavizar el cálculo de la pendiente
    punto_ref = None
    dist_ref = 0.0

    for track in gpx.tracks:
        for segment in track.segments:
            for punto in segment.points:
                
                # Calculamos distancia con el punto anterior
                if punto_anterior is not None:
                    dist_delta = punto.distance_2d(punto_anterior)
                    if dist_delta:
                        distancia_acumulada += dist_delta
                        
                # Inicializamos el primer punto
                if punto_ref is None:
                    punto_ref = punto
                    datos.append({'distancia_x': 0, 'inclinacion': 0.0})
                
                # Si hemos avanzado el intervalo (ej. 100m), calculamos la pendiente
                elif distancia_acumulada - dist_ref >= intervalo_m:
                    dist_tramo = distancia_acumulada - dist_ref
                    elev_tramo = punto.elevation - punto_ref.elevation
                    
                    # Pendiente = (Diferencia de altura / Distancia recorrida)
                    inclinacion = elev_tramo / dist_tramo if dist_tramo > 0 else 0.0
                    
                    datos.append({
                        'distancia_x': int(distancia_acumulada),
                        'inclinacion': round(inclinacion, 4)
                    })
                    
                    # Actualizamos las referencias para el siguiente bloque
                    punto_ref = punto
                    dist_ref = distancia_acumulada
                    
                punto_anterior = punto

    # Guardar los datos limpios en el CSV
    df = pd.DataFrame(datos)
    df.to_csv(archivo_csv, index=False)
    
    distancia_total_km = distancia_acumulada / 1000
    print(f"¡Éxito! Etapa de {distancia_total_km:.2f} km convertida.")
    print(f"Guardado como: {archivo_csv}")

if __name__ == "__main__":
    archivo_entrada = "_Tour_de_France_stage_21_.gpx" 
    archivo_salida = "etapa21_tour.csv"
    
    try:
        convertir_gpx_a_csv(archivo_entrada, archivo_salida, intervalo_m=100)
    except FileNotFoundError:
        print(f"Error: No se encuentra el archivo '{archivo_entrada}'. Añádelo a la carpeta.")