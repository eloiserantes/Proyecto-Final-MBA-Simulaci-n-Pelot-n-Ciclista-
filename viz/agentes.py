from .styles import COLORES_EQUIPOS

# Tamaño por defecto del círculo (radio normalizado 0–1)
_R_NORMAL   = 0.85
_R_AGOTADO  = 0.55

# Colores de estado/jerarquía (reservados, no usados para equipos)
_COLOR_LIDER    = "gold"
_COLOR_SPRINTER = "#2ecc71"
_COLOR_AGOTADO  = "#e74c3c"
_COLOR_FUGA     = "white"


def agent_portrayal(agent) -> dict | None:
    """
    Devuelve el diccionario de representación visual que Mesa usa en el canvas.

    Prioridad de color:
      1. Agotado  → rojo (independiente del rol o equipo)
      2. Líder    → gold
      3. Sprinter → verde
      4. En Fuga  → blanco
      5. Gregario → color de su equipo (paleta de 18, sin rojo/verde/oro/blanco)

    Forma:
      · Círculo  → ciclista a rueda (por defecto)
      · Rectángulo → ciclista tirando (en cabeza de grupo)
    """
    if agent is None:
        return None

    portrayal = {
        "Shape":  "circle",
        "Filled": "true",
        "Layer":  1,
        "r":      _R_NORMAL,
    }

    # ── Color según estado y rol ──────────────────────────────────────────
    if agent.energia < agent.umbral_fatiga:
        portrayal["Color"] = _COLOR_AGOTADO
        portrayal["r"]     = _R_AGOTADO
    elif agent.rol == "Lider":
        portrayal["Color"] = _COLOR_LIDER
    elif agent.rol == "Sprinter":
        portrayal["Color"] = _COLOR_SPRINTER
    elif agent.estado_tactico == "fuga":
        portrayal["Color"] = _COLOR_FUGA
    else:
        portrayal["Color"] = COLORES_EQUIPOS[(agent.equipo - 1) % len(COLORES_EQUIPOS)]

    # ── Forma según posición táctica ─────────────────────────────────────
    if agent.estado_tactico == "tirando":
        portrayal["Shape"] = "rect"
        portrayal["w"]     = _R_NORMAL
        portrayal["h"]     = _R_NORMAL

    return portrayal
