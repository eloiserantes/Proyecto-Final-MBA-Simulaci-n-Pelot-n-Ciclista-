from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Choice, Slider

from etapa_ciclista import EtapaModel

from viz import (
    COLORES_EQUIPOS,
    agent_portrayal,
    CabeceraEmision,
    LeyendaVisual,
    PerfilEtapaVisual,
    CabeceraVistaCenital,
    CabeceraGraficas,
    EtiquetaGrafica,
)


# =============================================================================
#  CANVAS (vista cenital del pelotón)
# =============================================================================

LARGO_PISTA = 200
ANCHO_PISTA = 5

grid = CanvasGrid(agent_portrayal, LARGO_PISTA, ANCHO_PISTA, 2000, 180)


# =============================================================================
#  GRÁFICAS DE ENERGÍA
# =============================================================================

chart_roles = ChartModule(
    [
        {"Label": "Energia Media Total", "Color": "#aaaaaa"},
        {"Label": "Energia Lideres",     "Color": "gold"},
        {"Label": "Energia Sprinters",   "Color": "#2ecc71"},
        {"Label": "Energia Gregarios",   "Color": "#00bcd4"},
    ],
    data_collector_name="datacollector",
    canvas_height=200,
    canvas_width=500,
)

chart_equipos = ChartModule(
    [{"Label": f"Equipo {i + 1}", "Color": COLORES_EQUIPOS[i]} for i in range(18)],
    data_collector_name="datacollector",
    canvas_height=250,
    canvas_width=500,
)

chart_gasto = ChartModule(
    [
        {"Label": "Gasto Gregarios", "Color": "#00bcd4"},
        {"Label": "Gasto Sprinters", "Color": "#2ecc71"},
        {"Label": "Gasto Lideres",   "Color": "gold"},
    ],
    data_collector_name="datacollector",
    canvas_height=200,
    canvas_width=500,
)


# =============================================================================
#  PARÁMETROS INTERACTIVOS
# =============================================================================

model_params = {
    "N_ciclistas":        144,
    "archivo_perfil_csv": "etapa21_tour.csv",

    "viento_direccion": Choice(
        "Dirección del Viento",
        value="lateral_izq",
        choices=["nulo", "a_favor", "en_contra", "lateral_izq", "lateral_der"],
    ),

    "viento_velocidad": Slider(
        "Velocidad del Viento (m/s)",
        value=5.0, min_value=0.0, max_value=20.0, step=1.0,
    ),
}


# =============================================================================
#  SERVIDOR MESA
# =============================================================================

server = ModularServer(
    EtapaModel,
    [
        CabeceraEmision(),
        LeyendaVisual(),
        PerfilEtapaVisual(),
        CabeceraVistaCenital(),
        grid,
        CabeceraGraficas(),

        # Gráfica 1: Reserva de Energía por Roles
        EtiquetaGrafica("Reserva de Energía por Roles", "Energía Restante (Julios)"),
        chart_roles,

        # Gráfica 2: Reserva de Energía por Equipos
        EtiquetaGrafica("Reserva de Energía por Equipos", "Energía Restante (Julios)"),
        chart_equipos,

        # Gráfica 3: Gasto Acumulado y Esfuerzo
        EtiquetaGrafica("Gasto Acumulado y Esfuerzo", "Julios Quemados (Trabajo)"),
        chart_gasto,
    ],
    "Simulación Pelotón Ciclista (ABM)",
    model_params,
)

EtapaModel.servidor_mesa = server

server.port = 8521
server.launch()
