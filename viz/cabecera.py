# =============================================================================
#  viz/cabecera.py
#  Bloque 1 · Cabecera HUD de emisión (distancia, progreso, viento, energía)
# =============================================================================

from mesa.visualization.modules import TextElement
from .styles import get_css_injection


# Mapeo de dirección de viento → (icono, color, etiqueta)
_ICONOS_VIENTO = {
    "nulo":        ("🌫️",   "#7f8c8d", "Sin Viento"),
    "a_favor":     ("🌬️→",  "#2ecc71", "Viento a Favor"),
    "en_contra":   ("←🌬️", "#e74c3c", "Viento en Contra"),
    "lateral_izq": ("🌬️↓",  "#f5c400", "Lateral Izq."),
    "lateral_der": ("🌬️↑",  "#f5c400", "Lateral Der."),
}


def _html_km_contador(km_recorrido: float, km_total: float, km_restante: float) -> str:
    return f"""
        <div style="
            background: var(--panel); border: 1px solid var(--panel-borde);
            border-radius: var(--radio); padding: 14px 20px; min-width: 180px;
            display: flex; flex-direction: column; justify-content: center;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
        ">
            <div style="color:var(--gris); font-size:0.75em; letter-spacing:2px;
                        text-transform:uppercase; margin-bottom:4px;">Distancia</div>
            <div style="color:var(--amarillo); font-size:2.6em; font-weight:900;
                        line-height:1; letter-spacing:-1px;">
                {km_recorrido:.1f}
                <span style="font-size:0.45em; color:var(--gris-claro); margin-left:4px;">
                    / {km_total:.0f} km
                </span>
            </div>
            <div style="color:var(--gris-claro); font-size:0.85em; margin-top:6px;">
                🏁 {km_restante:.1f} km restantes
            </div>
        </div>"""


def _html_barra_progreso(progreso_pct: float, km_total: float) -> str:
    return f"""
        <div style="flex:2; min-width:260px; display:flex; flex-direction:column;
                    justify-content:center; gap:8px;">
            <div style="display:flex; justify-content:space-between; align-items:baseline;">
                <span style="color:var(--gris); font-size:0.75em; letter-spacing:2px;
                             text-transform:uppercase;">Progreso de Etapa</span>
                <span style="color:var(--blanco); font-size:1.1em; font-weight:700;">
                    {progreso_pct:.1f}%
                </span>
            </div>
            <div style="background:#1e1e2e; border-radius:100px; height:14px;
                        border:1px solid var(--panel-borde); overflow:hidden; position:relative;">
                <div style="width:{progreso_pct:.1f}%; height:100%;
                            background:linear-gradient(90deg,var(--amarillo2),var(--amarillo));
                            border-radius:100px; box-shadow:0 0 10px rgba(245,196,0,0.5);
                            transition:width 0.3s ease;"></div>
            </div>
            <div style="display:flex; justify-content:space-between;
                        color:var(--gris); font-size:0.7em;">
                <span>KM 0</span>
                <span>KM {km_total*0.25:.0f}</span>
                <span>KM {km_total*0.5:.0f}</span>
                <span>KM {km_total*0.75:.0f}</span>
                <span>KM {km_total:.0f}</span>
            </div>
        </div>"""


def _html_viento(wind_ico: str, wind_color: str, wind_label: str,
                 velocidad: float) -> str:
    return f"""
        <div style="
            background:var(--panel); border:1px solid var(--panel-borde);
            border-radius:var(--radio); padding:14px 20px; min-width:140px;
            display:flex; flex-direction:column; justify-content:center;
            align-items:center; text-align:center;
        ">
            <div style="color:var(--gris); font-size:0.75em; letter-spacing:2px;
                        text-transform:uppercase; margin-bottom:6px;">Viento</div>
            <div style="font-size:2em;">{wind_ico}</div>
            <div style="color:{wind_color}; font-weight:700; font-size:0.95em;
                        margin-top:4px;">{wind_label}</div>
            <div style="color:var(--gris-claro); font-size:0.9em;">{velocidad:.0f} m/s</div>
        </div>"""


def _html_energia_media(energia_media_pct: float, color_energia: str) -> str:
    return f"""
        <div style="
            background:var(--panel); border:1px solid var(--panel-borde);
            border-radius:var(--radio); padding:14px 20px; min-width:150px;
            display:flex; flex-direction:column; justify-content:center;
            align-items:center; text-align:center;
        ">
            <div style="color:var(--gris); font-size:0.75em; letter-spacing:2px;
                        text-transform:uppercase; margin-bottom:6px;">Energía Media</div>
            <div style="font-size:2em; font-weight:900; color:{color_energia};
                        text-shadow:0 0 12px {color_energia}88;">
                {energia_media_pct:.0f}%
            </div>
            <div style="width:60px; height:8px; background:#1e1e2e; border-radius:100px;
                        margin-top:8px; overflow:hidden; border:1px solid var(--panel-borde);">
                <div style="width:{energia_media_pct:.0f}%; height:100%;
                            background:{color_energia}; border-radius:100px;"></div>
            </div>
            <div style="color:var(--gris); font-size:0.75em; margin-top:4px;">del pelotón</div>
        </div>"""


class CabeceraEmision(TextElement):
    """HUD superior: marca de emisión, km, progreso, viento y energía del pelotón."""

    def render(self, model) -> str:
        css = get_css_injection()

        # ── Progreso ──────────────────────────────────────────────────────
        progreso_pct = min(100.0, (model.distancia_carrera_global / model.longitud_etapa) * 100)
        km_recorrido = model.distancia_carrera_global / 1000
        km_total     = model.longitud_etapa / 1000
        km_restante  = max(0.0, km_total - km_recorrido)

        # ── Viento ────────────────────────────────────────────────────────
        wind_ico, wind_color, wind_label = _ICONOS_VIENTO.get(
            model.viento_direccion, ("💨", "#7f8c8d", model.viento_direccion)
        )

        # ── Energía media pelotón ─────────────────────────────────────────
        energias = [a.energia for a in model.schedule.agents]
        energia_media_pct = (sum(energias) / len(energias) / 2_000_000) * 100 if energias else 0
        color_energia = (
            "#2ecc71" if energia_media_pct > 50 else
            "#f5c400" if energia_media_pct > 25 else
            "#e74c3c"
        )

        tick = model.schedule.steps

        return f"""{css}
<div style="
    font-family:var(--fuente-disp);
    background:linear-gradient(135deg,var(--carbon) 0%,#0d0d16 100%);
    border:1px solid var(--panel-borde); border-top:4px solid var(--amarillo);
    border-radius:0 0 var(--radio) var(--radio);
    padding:0; margin-bottom:4px;
    box-shadow:var(--sombra),var(--sombra-glow); overflow:hidden;
">
    <!-- FRANJA SUPERIOR -->
    <div style="background:var(--amarillo); padding:5px 20px;
                display:flex; align-items:center; justify-content:space-between;">
        <span style="color:var(--negro); font-weight:900; font-size:1.1em;
                     letter-spacing:2px; text-transform:uppercase;">
            SIMULACIÓN PELOTÓN CICLISTA - PRO TEAM
        </span>
        <span style="color:var(--negro); font-weight:600; font-size:0.9em;">
            TICK #{tick:,}
        </span>
    </div>

    <!-- CUERPO PRINCIPAL -->
    <div style="padding:18px 24px; display:flex; gap:24px;
                align-items:stretch; flex-wrap:wrap;">
        {_html_km_contador(km_recorrido, km_total, km_restante)}
        {_html_barra_progreso(progreso_pct, km_total)}
        {_html_viento(wind_ico, wind_color, wind_label, model.viento_velocidad)}
        {_html_energia_media(energia_media_pct, color_energia)}
    </div>
</div>
"""
