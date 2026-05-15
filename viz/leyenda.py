from mesa.visualization.modules import TextElement
from .styles import COLORES_EQUIPOS, badge_equipo


# -----------------------------------------------------------------------------
#  Helpers HTML internos
# -----------------------------------------------------------------------------

def _stat_badge(label: str, valor, color: str, bg: str) -> str:
    return f"""
    <div style="background:{bg}; border:1px solid rgba(120,120,120,0.2);
                border-radius:6px; padding:10px 16px; text-align:center;
                min-width:90px; flex:1;">
        <div style="color:{color}; font-size:1.6em; font-weight:900;
                    font-family:'Barlow Condensed',sans-serif;">{valor}</div>
        <div style="color:#7f8c8d; font-weight:bold; font-size:0.72em;
                    letter-spacing:1px; text-transform:uppercase; margin-top:2px;">
            {label}
        </div>
    </div>"""


def _leyenda_item(forma: str, color: str, titulo: str, subtitulo: str) -> str:
    return f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
        <div style="color:{color}; font-size:1.4em; width:20px; text-align:center;
                    text-shadow:0 0 4px rgba(120,120,120,0.3);">{forma}</div>
        <div style="line-height:1.2;">
            <div style="color:#555; font-weight:800; font-size:0.9em;">{titulo}</div>
            <div style="color:#7f8c8d; font-size:0.8em;">{subtitulo}</div>
        </div>
    </div>"""


# -----------------------------------------------------------------------------
#  Secciones de la leyenda
# -----------------------------------------------------------------------------

def _seccion_postura() -> str:
    return f"""
    <div style="flex:1; min-width:200px;
                border-right:1px solid rgba(120,120,120,0.2); padding-right:15px;">
        <div style="color:#222; font-size:0.8em; font-weight:900; letter-spacing:1px;
                    text-transform:uppercase; margin-bottom:12px;">
            1. Postura (La Forma)
        </div>
        {_leyenda_item("●", "#7F8C8D", "Círculo = A Rueda",
                        "Protegido del viento (Ahorra energía)")}
        {_leyenda_item("■", "#7F8C8D", "Cuadrado = En Cabeza",
                        "Cortando el viento (Gasto máximo)")}
    </div>"""


def _seccion_jerarquia() -> str:
    return f"""
    <div style="flex:1; min-width:200px;
                border-right:1px solid rgba(120,120,120,0.2); padding-right:15px;">
        <div style="color:#222; font-size:0.8em; font-weight:900; letter-spacing:1px;
                    text-transform:uppercase; margin-bottom:12px;">
            2. Jerarquía y Estado
        </div>
        {_leyenda_item("●", "gold",    "Líder",     "El protegido del equipo")}
        {_leyenda_item("●", "#2ecc71", "Sprinter",  "Especialista final")}
        {_leyenda_item("●", "#e74c3c", "Agotado",   "Sin energía, se descuelga")}
        {_leyenda_item("●", "white",   "En Fuga",   "Atacando en solitario (Blanco)")}
    </div>"""


def _seccion_equipos() -> str:
    badges = "".join(
        badge_equipo(i, c) for i, c in enumerate(COLORES_EQUIPOS)
    )
    return f"""
    <div style="flex:1.2; min-width:250px;">
        <div style="color:#222; font-size:0.8em; font-weight:900; letter-spacing:1px;
                    text-transform:uppercase; margin-bottom:12px;">
            3. Los Equipos (Gregarios Frescos)
        </div>
        <div style="color:#7f8c8d; font-size:0.85em; margin-bottom:10px; line-height:1.4;">
            Los gregarios sanos se colorean según su equipo:
        </div>
        <div style="display:flex; gap:6px; flex-wrap:wrap;">
            {badges}
        </div>
    </div>"""


# -----------------------------------------------------------------------------
#  Clase Mesa
# -----------------------------------------------------------------------------

class LeyendaVisual(TextElement):
    """Panel de control con estadísticas en vivo y guía de colores/formas."""

    def render(self, model) -> str:
        agentes  = model.schedule.agents
        total    = len(agentes)
        agotados = sum(1 for a in agentes if a.energia < a.umbral_fatiga)
        en_fuga  = sum(1 for a in agentes if a.estado_tactico == "fuga")
        tirando  = sum(1 for a in agentes if a.estado_tactico == "tirando")
        lideres  = sum(1 for a in agentes if a.rol == "Lider")
        sprinters= sum(1 for a in agentes if a.rol == "Sprinter")
        gregarios= sum(1 for a in agentes if a.rol == "Gregario")

        stats = "".join([
            _stat_badge("Total",    total,     "#8E44AD", "rgba(142,68,173,0.08)"),
            _stat_badge("Líderes",  lideres,   "gold",    "rgba(245,196,0,0.08)"),
            _stat_badge("Sprinters",sprinters, "#2ecc71", "rgba(46,204,113,0.08)"),
            _stat_badge("Gregarios",gregarios, "#00bcd4", "rgba(0,188,212,0.08)"),
            _stat_badge("Tirando",  tirando,   "#34495E", "rgba(52,73,94,0.08)"),
            _stat_badge("En Fuga",  en_fuga,   "#2C3E50", "rgba(44,62,80,0.08)"),
            _stat_badge("Agotados", agotados,  "#e74c3c", "rgba(231,76,60,0.08)"),
        ])

        return f"""
<div style="font-family:'Barlow',sans-serif; border:1px solid rgba(120,120,120,0.2);
            border-radius:6px; padding:18px 22px; margin-bottom:6px;
            box-shadow:0 2px 10px rgba(0,0,0,0.05);">

    <div style="font-family:'Barlow Condensed',sans-serif; font-size:0.85em;
                font-weight:700; letter-spacing:2px; text-transform:uppercase;
                color:#111111; margin-bottom:14px;
                border-bottom:1px solid rgba(120,120,120,0.2); padding-bottom:8px;">
        Panel de Control &amp; Guía Visual
    </div>

    <!-- ESTADÍSTICAS EN VIVO -->
    <div style="display:flex; gap:8px; margin-bottom:16px; flex-wrap:wrap;">
        {stats}
    </div>

    <!-- LEYENDA DE COLORES Y FORMAS -->
    <div style="display:flex; gap:20px; flex-wrap:wrap;
                background:rgba(120,120,120,0.03); padding:15px;
                border-radius:6px; border:1px solid rgba(120,120,120,0.1);">
        {_seccion_postura()}
        {_seccion_jerarquia()}
        {_seccion_equipos()}
    </div>
</div>
"""
