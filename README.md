# Proyecto-Final-MBA-Simulación-Pelotón-Ciclista

Manual de instrucciones para la instalación y ejecución del proyecto de simulación de pelotón ciclista.

---

## Estructura del repositorio

```
Proyecto-Final-MBA-Simulaci-n-Pelot-n-Ciclista-/
│
├── viz/                                        ← Carpeta con el front-end (HTML)
│
├── README.md                                   ← Este archivo
├── Tour2025etapa1(Lille)2025062090735.gpx      ← Archivo GPX con la ruta
├── app.py                                      ← Archivo principal de ejecución
├── conversor_gpx.py                            ← Conversor de archivos GPX
├── etapa21_tour.csv                            ← Datos de la etapa ciclista
└── etapa_ciclista.py                           ← Lógica de la simulación
```

## Instrucciones de uso

### 1. Coloca todos los archivos en la misma carpeta

Es **obligatorio** que todos los archivos del repositorio se encuentren en el mismo directorio raíz. El proyecto no funcionará correctamente si los archivos están dispersos en carpetas distintas.

*Nota*: No es necesario descargarse el conversosr de archivos GPX ni el .gpx para el correcto funcionamiento de la práctica. Los dejó ahí porque se ha empleado en la práctic y por si se quiere probar a convertir ese archivo a un csv con los datos de la etapa.

### 2. No muevas los archivos de la carpeta `viz`

La carpeta `viz` contiene los archivos HTML que conforman la interfaz visual del proyecto (front-end). **No extraigas ni muevas ningún archivo de esta carpeta**, ya que el sistema los referencia desde su ubicación original. Si se modificara su ubicación, la interfaz no cargará correctamente.

### 3. Ejecuta el proyecto

Abre una terminal y navega hasta el directorio donde tengas guardada la carpeta con todos los archivos del repositorio. A continuación, ejecuta el siguiente comando:

```bash
python app.py
```

Al ejecutarse, el programa debería **abrir automáticamente** la interfaz en tu navegador por defecto.

> **¿No se abrió el navegador automáticamente?**  
> Si la interfaz no se abre sola, copia y pega la siguiente URL en tu navegador manualmente:
>
> [http://127.0.0.1:8521](http://127.0.0.1:8521)

---

## Descripción de los archivos

| Archivo / Carpeta | Descripción |
|---|---|
| `viz/` | Carpeta con los archivos HTML del front-end. No mover su contenido. |
| `app.py` | Punto de entrada principal. Ejecutar con `python app.py`. |
| `etapa_ciclista.py` | Contiene la lógica principal de la simulación del pelotón. |
| `conversor_gpx.py` | Herramienta para convertir y procesar archivos GPX. |
| `Tour2025etapa1(Lille)2025062090735.gpx` | Archivo con los datos de la ruta GPS de la etapa. |
| `etapa21_tour.csv` | Dataset con información de la etapa ciclista. |

---

## Sobre el proyecto

Este proyecto simula el comportamiento de un pelotón ciclista como parte del Proyecto Final del MBA. Utiliza datos reales de una etapa del Tour de Francia para modelar y visualizar la dinámica del grupo de ciclistas en tiempo real a través de una interfaz web interactiva.
