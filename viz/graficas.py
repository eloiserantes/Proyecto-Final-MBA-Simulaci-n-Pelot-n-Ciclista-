from mesa.visualization.modules import TextElement
from .styles import COLORES_EQUIPOS, color_equipo


# =============================================================================
# RANKING EFICIENCIA ENERGÉTICA (18 EQUIPOS)
# =============================================================================

def _energia_media_equipo(model, eq_id: int) -> float:
    vals = [a.energia for a in model.schedule.agents if a.equipo == eq_id]
    return sum(vals) / len(vals) if vals else 0.0


def _badge_equipo_ranking(idx: int, eq_id: int, ener: float,
                           color: str, medalla: str) -> str:
    pct           = (ener / 2_000_000) * 100
    borde_opacity = "99" if idx < 3 else "44"
    bg_opacity    = "22" if idx < 3 else "0e"
    font_size     = "1.1em" if idx < 3 else "0.85em"
    bar_pct       = min(pct, 100)

    return f"""
    <div style="
        background:{color}{bg_opacity}; border:1px solid {color}{borde_opacity};
        border-radius:var(--radio); padding:5px 10px;
        display:flex; align-items:center; gap:7px;
        font-family:var(--fuente-disp); min-width:155px;
    ">
        <span style="font-size:{font_size}; min-width:22px; text-align:center;">
            {medalla}
        </span>
        <div style="flex:1;">
            <div style="color:{color}; font-weight:700; font-size:0.88em;
                        text-shadow:0 1px 2px rgba(0,0,0,0.8);">
                Equipo {eq_id}
            </div>
            <div style="color:var(--gris-claro); font-size:0.75em;">
                {pct:.1f}% energía
            </div>
        </div>
        <div style="width:40px; height:5px; background:#1e1e2e;
                    border-radius:100px; overflow:hidden; flex-shrink:0;">
            <div style="width:{bar_pct:.0f}%; height:100%;
                        background:{color}; border-radius:100px;"></div>
        </div>
    </div>"""


class CabeceraGraficas(TextElement):
    """Ranking en vivo de los 18 equipos por eficiencia energética."""

    _MEDALLAS = ["1º", "2º", "3º"] + [f"{i + 1}º" for i in range(3, 18)]

    def render(self, model) -> str:
        equipos_ids = sorted({a.equipo for a in model.schedule.agents})

        ranking = sorted(
            [(eq_id, _energia_media_equipo(model, eq_id)) for eq_id in equipos_ids],
            key=lambda x: x[1],
            reverse=True,
        )

        badges = "".join(
            _badge_equipo_ranking(
                idx, eq_id, ener,
                color_equipo(eq_id),
                self._MEDALLAS[idx],
            )
            for idx, (eq_id, ener) in enumerate(ranking)
        )

        return f"""
<div style="
    font-family:var(--fuente-body); background:var(--carbon);
    border:1px solid var(--panel-borde); border-top:3px solid var(--amarillo);
    border-radius:var(--radio); padding:18px 22px;
    margin-top:18px; box-shadow:var(--sombra);
">
    <div style="font-family:var(--fuente-disp); font-size:0.75em; font-weight:700;
                letter-spacing:3px; text-transform:uppercase;
                color:var(--amarillo); margin-bottom:14px;">
        Ranking Eficiencia Energética — 18 Equipos
    </div>

    <div style="margin-bottom:10px; color:var(--gris-claro); font-size:0.88em; line-height:1.6;">
        Qué equipos optimizan mejor el <b>drafting</b> y la protección de sus líderes.
        <span style="color:var(--gris); font-size:0.85em;"> · Se actualiza en directo.</span>
    </div>

    <div style="display:flex; gap:8px; flex-wrap:wrap;">
        {badges}
    </div>

    <div style="height:2px;
                background:linear-gradient(90deg,transparent,var(--panel-borde) 20%,
                           var(--panel-borde) 80%,transparent);
                margin-top:14px;"></div>
</div>
"""



# ETIQUETA DE EJES PARA CADA GRÁFICA
class EtiquetaGrafica(TextElement):
    """Cabecera descriptiva (título + ejes X/Y) que precede a cada ChartModule."""

    def __init__(self, titulo: str, eje_y: str,
                 eje_x: str = "Tiempo (Ticks / Segundos)"):
        self.titulo = titulo
        self.eje_y  = eje_y
        self.eje_x  = eje_x

    def render(self, model) -> str:
        return f"""
<div style="
    background:linear-gradient(90deg,#0d0d14,var(--carbon));
    border:1px solid var(--panel-borde); border-bottom:2px solid var(--verde);
    border-radius:var(--radio) var(--radio) 0 0;
    padding:8px 22px; margin-top:25px;
    display:flex; justify-content:space-between; align-items:center;
">
    <div style="color:var(--verde); font-size:0.85em; font-weight:bold;
                width:180px; text-align:left; line-height:1.2;">
        ▲ EJE Y:<br>
        <span style="color:var(--gris-claro); font-weight:normal;">{self.eje_y}</span>
    </div>
    <div style="color:var(--blanco); font-size:1.1em; font-family:var(--fuente-disp);
                font-weight:900; letter-spacing:2px; text-transform:uppercase;
                text-align:center; flex:1;">
        {self.titulo}
    </div>
    <div style="color:var(--verde); font-size:0.85em; font-weight:bold;
                width:180px; text-align:right; line-height:1.2;">
        EJE X: ▶<br>
        <span style="color:var(--gris-claro); font-weight:normal;">{self.eje_x}</span>
    </div>
</div>
"""
