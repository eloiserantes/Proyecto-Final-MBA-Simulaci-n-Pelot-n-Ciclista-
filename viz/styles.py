# -----------------------------------------------------------------------------
#  PALETA DE EQUIPOS
#  18 tonos diferenciados de los colores de estado/jerarquía reservados:
#    · Rojo   (#e74c3c) → Agotado
#    · Verde  (#2ecc71) → Sprinter
#    · Amarillo (gold)  → Líder
#    · Blanco           → En Fuga
# -----------------------------------------------------------------------------

COLORES_EQUIPOS: list[str] = [
    "#1565C0",  # 1  Azul marino oscuro
    "#6A1B9A",  # 2  Púrpura profundo
    "#00838F",  # 3  Teal oscuro
    "#4527A0",  # 4  Índigo intenso
    "#283593",  # 5  Azul real
    "#00695C",  # 6  Verde pizarra (oscuro, ≠ verde estado)
    "#558B2F",  # 7  Verde oliva oscuro
    "#F57F17",  # 8  Ámbar oscuro
    "#E65100",  # 9  Naranja quemado
    "#4E342E",  # 10 Marrón chocolate
    "#37474F",  # 11 Gris pizarra
    "#AD1457",  # 12 Rosa frambuesa oscuro
    "#0277BD",  # 13 Azul cielo profundo
    "#6D4C41",  # 14 Café medio
    "#0D47A1",  # 15 Azul cobalto
    "#880E4F",  # 16 Magenta oscuro
    "#1B5E20",  # 17 Verde cazador (oscuro, ≠ verde estado)
    "#BF360C",  # 18 Rojo ladrillo oscuro (≠ rojo estado brillante)
]


# -----------------------------------------------------------------------------
#  CSS GLOBAL  (inyectado una sola vez en el <head> de Mesa)
# -----------------------------------------------------------------------------

CSS_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;900&family=Barlow:wght@300;400;500&display=swap');

:root {
    --negro:       #0a0a0f;
    --carbon:      #13131a;
    --panel:       #1a1a24;
    --panel-borde: #252535;
    --amarillo:    #f5c400;
    --amarillo2:   #e0a800;
    --verde:       #2ecc71;
    --verde-mont:  #27ae60;
    --rojo:        #e74c3c;
    --rojo-claro:  #ff6b6b;
    --azul:        #3498db;
    --morado:      #9b59b6;
    --cian:        #1abc9c;
    --rosa:        #e91e8c;
    --gris:        #7f8c8d;
    --gris-claro:  #bdc3c7;
    --blanco:      #ecf0f1;
    --fuente-disp: 'Barlow Condensed', sans-serif;
    --fuente-body: 'Barlow', sans-serif;
    --radio:       6px;
    --sombra:      0 4px 20px rgba(0,0,0,0.6);
    --sombra-glow: 0 0 18px rgba(245,196,0,0.25);
}

body, .modular-server {
    background-color: #ffffff !important;
    font-family: var(--fuente-body) !important;
    color: var(--negro) !important;
}

canvas { border-radius: var(--radio); }

/* Ocultar el título por defecto de Mesa y usar el nuestro */
h1 { display: none !important; }
"""

# -----------------------------------------------------------------------------
#  Inyección única de CSS (evita duplicados en cada tick de Mesa)
# -----------------------------------------------------------------------------

_css_inyectado = False


def get_css_injection() -> str:
    """Devuelve el bloque <style> la primera vez; cadena vacía en adelante."""
    global _css_inyectado
    if _css_inyectado:
        return ""
    _css_inyectado = True
    return f"<style>{CSS_BASE}</style>"


# -----------------------------------------------------------------------------
#  Helpers HTML reutilizables
# -----------------------------------------------------------------------------

def color_equipo(eq_id: int) -> str:
    """Devuelve el color hex del equipo (1-18)."""
    return COLORES_EQUIPOS[(eq_id - 1) % len(COLORES_EQUIPOS)]


def badge_equipo(idx: int, color: str) -> str:
    """Pequeño badge numerado para la leyenda de equipos."""
    return (
        f'<div style="background:{color}; color:#fff; font-size:0.75em; '
        f'font-weight:900; padding:4px 8px; border-radius:4px; min-width:35px; '
        f'text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.3); '
        f'text-shadow:0 1px 2px rgba(0,0,0,0.9), 0 0 6px rgba(0,0,0,0.6);">'
        f'{idx + 1}</div>'
    )
