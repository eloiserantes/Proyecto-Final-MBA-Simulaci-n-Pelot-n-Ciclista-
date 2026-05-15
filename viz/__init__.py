from .styles   import COLORES_EQUIPOS, color_equipo
from .agentes  import agent_portrayal
from .cabecera import CabeceraEmision
from .leyenda  import LeyendaVisual
from .perfil   import PerfilEtapaVisual, CabeceraVistaCenital
from .graficas import CabeceraGraficas, EtiquetaGrafica

__all__ = [
    # Paleta compartida
    "COLORES_EQUIPOS",
    "color_equipo",
    # Canvas
    "agent_portrayal",
    # Bloques de UI
    "CabeceraEmision",
    "LeyendaVisual",
    "PerfilEtapaVisual",
    "CabeceraVistaCenital",
    "CabeceraGraficas",
    "EtiquetaGrafica",
]
