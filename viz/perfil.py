# =============================================================================
#  viz/perfil.py
#  Bloque 3 · Perfil de etapa SVG con posición del pelotón
#  Bloque 4 · Cabecera de la vista cenital (Helicóptero)
# =============================================================================

from mesa.visualization.modules import TextElement



def _calcular_gradient_stops(elevaciones: dict, dist_max: float,
                              elev_max: float) -> str:
    """Genera los <stop> de color del gradiente del perfil por altitud."""
    stops = ""
    for dist in sorted(elevaciones):
        elev = elevaciones[dist]
        pct  = (dist / dist_max) * 100
        r    = int(46  + (elev / elev_max) * 150)
        g    = int(139 + (elev / elev_max) * 60)
        b    = int(87  - (elev / elev_max) * 50)
        stops += f'<stop offset="{pct:.1f}%" stop-color="rgb({r},{g},{b})" stop-opacity="0.55"/>'
    return stops


def _dibujar_cuadricula_y(svg: str, ah: float, mg_izq: int,
                           ancho: int, elev_max: float) -> str:
    paso_elev = 50
    cota = paso_elev
    while cota <= elev_max:
        y_l = ah - (cota / elev_max) * ah
        svg += (
            f'<line x1="{mg_izq}" y1="{y_l:.1f}" x2="{ancho}" y2="{y_l:.1f}" '
            f'stroke="#2a2a3a" stroke-dasharray="4 3"/>'
            f'<text x="4" y="{y_l + 4:.1f}" fill="#555" '
            f'font-family="Barlow Condensed,sans-serif" font-size="11">{int(cota)}m</text>'
        )
        cota += paso_elev
    return svg


def _dibujar_cuadricula_x(svg: str, ah: float, mg_izq: int, aw: float,
                           dist_max: float) -> str:
    paso_d = 20_000
    marca  = 0
    while marca <= dist_max:
        x_m = mg_izq + (marca / dist_max) * aw
        svg += (
            f'<line x1="{x_m:.1f}" y1="0" x2="{x_m:.1f}" y2="{ah}" '
            f'stroke="#1e1e2e" stroke-dasharray="3 4"/>'
            f'<line x1="{x_m:.1f}" y1="{ah}" x2="{x_m:.1f}" y2="{ah + 6}" '
            f'stroke="#555" stroke-width="1.5"/>'
            f'<text x="{x_m - 8:.1f}" y="{ah + 20}" fill="#666" '
            f'font-family="Barlow Condensed,sans-serif" font-size="11">'
            f'{int(marca / 1000)}km</text>'
        )
        marca += paso_d
    return svg


def _agrupar_ciclistas(agentes, umbral_m: float = 150.0) -> list:
    """Agrupa ciclistas por proximidad en la carrera para dibujar burbujas."""
    ordenados = sorted(agentes, key=lambda c: c.distancia_absoluta, reverse=True)
    grupos, grupo_act, dist_ref = [], [], -1
    for c in ordenados:
        if not grupo_act:
            grupo_act, dist_ref = [c], c.distancia_absoluta
        elif abs(dist_ref - c.distancia_absoluta) <= umbral_m:
            grupo_act.append(c)
        else:
            grupos.append(grupo_act)
            grupo_act, dist_ref = [c], c.distancia_absoluta
    if grupo_act:
        grupos.append(grupo_act)
    return grupos


def _color_grupo(grupo: list) -> str:
    if any(c.energia < c.umbral_fatiga for c in grupo):
        return "#e74c3c"
    if len(grupo) > 15:
        return "white"
    if any(c.rol == "Lider" for c in grupo):
        return "#f5c400"
    if any(c.estado_tactico == "fuga" for c in grupo):
        return "white"
    return "#00bcd4"


def _tooltip_grupo(grupo: list, dm: float) -> str:
    tip = f"km {dm / 1000:.2f}  |  {len(grupo)} ciclistas&#10;"
    tip += "─────────────────────&#10;"
    for c in grupo[:6]:
        lleno = int(c.energia / c.energia_maxima * 8)
        bar   = "█" * lleno + "░" * (8 - lleno)
        tip  += f"Eq.{c.equipo} {c.rol:8s} [{bar}]&#10;"
    if len(grupo) > 6:
        tip += f"  … y {len(grupo) - 6} más"
    return tip


class PerfilEtapaVisual(TextElement):
    """SVG interactivo del perfil altimétrico con posición en vivo del pelotón."""

    ANCHO   = 980
    ALTO    = 210
    MG_IZQ  = 55
    MG_INF  = 32

    def render(self, model) -> str:
        ancho, alto = self.ANCHO, self.ALTO
        mg_izq, mg_inf = self.MG_IZQ, self.MG_INF
        aw = ancho - mg_izq
        ah = alto  - mg_inf

        dist_max = max(100.0, model.longitud_etapa)
        elev_max = max(10.0,  model.elevacion_maxima * 1.18)

        # ── Polígono del perfil ───────────────────────────────────────────
        puntos = [f"{mg_izq},{ah}"]
        for dist in sorted(model.elevaciones):
            elev = model.elevaciones[dist]
            x = mg_izq + (dist / dist_max) * aw
            y = ah - (elev / elev_max) * ah
            puntos.append(f"{x:.1f},{y:.1f}")
        puntos.append(f"{mg_izq + aw},{ah}")
        puntos_str = " ".join(puntos)

        x_carrera = mg_izq + (model.distancia_carrera_global / dist_max) * aw
        gradient_stops = _calcular_gradient_stops(model.elevaciones, dist_max, elev_max)

        # ── Construcción del SVG ─────────────────────────────────────────
        svg = f"""
<div style="
    font-family:var(--fuente-body); background:var(--carbon);
    border:1px solid var(--panel-borde); border-radius:var(--radio);
    padding:16px 20px; margin-bottom:6px; box-shadow:var(--sombra);
">
    <div style="font-family:var(--fuente-disp); font-size:0.75em; font-weight:700;
                letter-spacing:3px; text-transform:uppercase;
                color:var(--verde); margin-bottom:10px;">
        Perfil de Etapa · Posición del Pelotón
    </div>

    <svg width="100%" height="auto" viewBox="0 0 {ancho} {alto}"
         style="background:#0d0d14; border:1px solid var(--panel-borde);
                border-radius:4px; display:block;">
        <defs>
            <linearGradient id="perfilGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                {gradient_stops}
            </linearGradient>
            <filter id="glow">
                <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
"""
        svg = _dibujar_cuadricula_y(svg, ah, mg_izq, ancho, elev_max)
        svg = _dibujar_cuadricula_x(svg, ah, mg_izq, aw, dist_max)

        # Ejes
        svg += (
            f'<line x1="{mg_izq}" y1="0" x2="{mg_izq}" y2="{ah}" stroke="#444" stroke-width="1.5"/>'
            f'<line x1="{mg_izq}" y1="{ah}" x2="{ancho}" y2="{ah}" stroke="#444" stroke-width="1.5"/>'
        )

        # Polígono del perfil
        svg += f'<polygon points="{puntos_str}" fill="url(#perfilGrad)"/>'

        # Línea de posición actual
        svg += f'''
        <line x1="{x_carrera:.1f}" y1="0" x2="{x_carrera:.1f}" y2="{ah}"
              stroke="#f5c400" stroke-width="2" stroke-dasharray="6 3" opacity="0.9"/>
        <polygon points="{x_carrera - 6:.1f},0 {x_carrera + 6:.1f},0 {x_carrera:.1f},12"
                 fill="#f5c400" opacity="0.95"/>'''

        # Burbujas de grupos de ciclistas
        for grupo in _agrupar_ciclistas(model.schedule.agents):
            dm   = sum(c.distancia_absoluta for c in grupo) / len(grupo)
            elev = model.obtener_elevacion(dm)
            xp   = mg_izq + (dm / dist_max) * aw
            yp   = ah - (elev / elev_max) * ah
            radio = min(9.0, 3.5 + len(grupo) * 0.09)
            color = _color_grupo(grupo)
            tip   = _tooltip_grupo(grupo, dm)

            svg += f'''
            <circle cx="{xp:.1f}" cy="{yp:.1f}" r="{radio:.1f}"
                    fill="{color}" opacity="0.92"
                    stroke="#0a0a0f" stroke-width="1.5"
                    filter="url(#glow)">
                <title>{tip}</title>
            </circle>'''

        svg += "</svg></div>"
        return svg


# =============================================================================
#  BLOQUE 4 · CABECERA VISTA CENITAL
# =============================================================================

_CATEGORIAS_PENDIENTE = [
    (8,   ("HC",     "#e74c3c")),
    (5,   ("Cat 1",  "#e74c3c")),
    (3,   ("Cat 2",  "#f5c400")),
    (1,   ("Cat 3",  "#2ecc71")),
]


def _categoria_pendiente(incl_pct: float) -> tuple[str, str]:
    for umbral, cat in _CATEGORIAS_PENDIENTE:
        if incl_pct > umbral:
            return cat
    if incl_pct < -1:
        return ("Bajada", "#3498db")
    return ("Llano", "#7f8c8d")


class CabeceraVistaCenital(TextElement):
    """Cabecera de la vista en planta: altitud, pendiente y categoría en vivo."""

    def render(self, model) -> str:
        elev_actual = model.obtener_elevacion(model.distancia_carrera_global)
        incl_actual = model.obtener_inclinacion_actual(model.distancia_carrera_global)
        incl_pct    = incl_actual * 100
        cat_label, cat_color = _categoria_pendiente(incl_pct)

        return f"""
<div style="
    font-family:var(--fuente-disp);
    background:linear-gradient(90deg,#0d0d14,var(--carbon));
    border:1px solid var(--panel-borde); border-bottom:none;
    border-radius:var(--radio) var(--radio) 0 0;
    padding:10px 22px; margin-top:16px;
    display:flex; justify-content:space-between; align-items:center;
    flex-wrap:wrap; gap:10px;
">
    <div style="text-align:left;">
        <div style="color:var(--verde); font-size:1em; font-weight:700; letter-spacing:1px;">
            ▲ Eje Y — Posición lateral
        </div>
        <div style="color:var(--gris); font-size:0.78em;">
            Carril 1 (cuneta izq.) → Carril 5 (cuneta der.)
        </div>
    </div>

    <div style="text-align:center;">
        <div style="color:var(--blanco); font-weight:900; font-size:1.3em;
                    text-transform:uppercase; letter-spacing:2px;">
            Vista Helicóptero
        </div>
        <div style="display:flex; gap:14px; justify-content:center;
                    margin-top:4px; font-size:0.85em;">
            <span style="color:var(--gris-claro);">
                Alt: <b style="color:var(--verde);">{elev_actual:.0f} m</b>
            </span>
            <span style="color:var(--gris-claro);">
                Pendiente: <b style="color:{cat_color};">{incl_pct:+.1f}%</b>
            </span>
            <span style="background:{cat_color}22; border:1px solid {cat_color};
                         color:{cat_color}; padding:1px 8px; border-radius:4px;
                         font-weight:700;">
                {cat_label}
            </span>
        </div>
    </div>

    <div style="text-align:right;">
        <div style="color:var(--amarillo); font-size:1em; font-weight:700; letter-spacing:1px;">
            Eje X ▶:
        </div>
        <div style="color:var(--gris); font-size:0.78em;">
            Sentido de Marcha ➡
        </div>
    </div>
</div>
"""
