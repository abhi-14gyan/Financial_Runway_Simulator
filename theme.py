import altair as alt
import streamlit as st

_DARK_PALETTE = {
    "BG": "#09090B",
    "CARD": "#111217",
    "CARD_SECONDARY": "#181A20",
    "BORDER": "rgba(255,255,255,.06)",
    "ACCENT": "#4F8CFF",
    "ACCENT_SECONDARY": "#6EE7FF",
    "SUCCESS": "#22C55E",
    "DANGER": "#EF4444",
    "WARNING": "#F59E0B",
    "TEXT_PRIMARY": "#FFFFFF",
    "TEXT_SECONDARY": "rgba(255,255,255,.72)",
    "TEXT_MUTED": "rgba(255,255,255,.45)",
    "CHART_DOMAIN": "rgba(255,255,255,.12)",
    "CHART_GRID": "rgba(255,255,255,.06)",
}

_LIGHT_PALETTE = {
    "BG": "#F7F8FA",
    "CARD": "#FFFFFF",
    "CARD_SECONDARY": "#F1F3F6",
    "BORDER": "rgba(0,0,0,.08)",
    "ACCENT": "#2563EB",
    "ACCENT_SECONDARY": "#0EA5E9",
    "SUCCESS": "#16A34A",
    "DANGER": "#DC2626",
    "WARNING": "#D97706",
    "TEXT_PRIMARY": "#0B0D12",
    "TEXT_SECONDARY": "rgba(11,13,18,.72)",
    "TEXT_MUTED": "rgba(11,13,18,.45)",
    "CHART_DOMAIN": "rgba(0,0,0,.15)",
    "CHART_GRID": "rgba(0,0,0,.08)",
}

BG = _DARK_PALETTE["BG"]
CARD = _DARK_PALETTE["CARD"]
CARD_SECONDARY = _DARK_PALETTE["CARD_SECONDARY"]
BORDER = _DARK_PALETTE["BORDER"]
ACCENT = _DARK_PALETTE["ACCENT"]
ACCENT_SECONDARY = _DARK_PALETTE["ACCENT_SECONDARY"]
SUCCESS = _DARK_PALETTE["SUCCESS"]
DANGER = _DARK_PALETTE["DANGER"]
WARNING = _DARK_PALETTE["WARNING"]
TEXT_PRIMARY = _DARK_PALETTE["TEXT_PRIMARY"]
TEXT_SECONDARY = _DARK_PALETTE["TEXT_SECONDARY"]
TEXT_MUTED = _DARK_PALETTE["TEXT_MUTED"]
CHART_DOMAIN = _DARK_PALETTE["CHART_DOMAIN"]
CHART_GRID = _DARK_PALETTE["CHART_GRID"]


def set_theme(dark: bool = True) -> None:
    global BG, CARD, CARD_SECONDARY, BORDER, ACCENT, ACCENT_SECONDARY
    global SUCCESS, DANGER, WARNING, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
    global CHART_DOMAIN, CHART_GRID
    palette = _DARK_PALETTE if dark else _LIGHT_PALETTE
    BG = palette["BG"]
    CARD = palette["CARD"]
    CARD_SECONDARY = palette["CARD_SECONDARY"]
    BORDER = palette["BORDER"]
    ACCENT = palette["ACCENT"]
    ACCENT_SECONDARY = palette["ACCENT_SECONDARY"]
    SUCCESS = palette["SUCCESS"]
    DANGER = palette["DANGER"]
    WARNING = palette["WARNING"]
    TEXT_PRIMARY = palette["TEXT_PRIMARY"]
    TEXT_SECONDARY = palette["TEXT_SECONDARY"]
    TEXT_MUTED = palette["TEXT_MUTED"]
    CHART_DOMAIN = palette["CHART_DOMAIN"]
    CHART_GRID = palette["CHART_GRID"]

ICONS = {
    "wallet": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"/><path d="M3 5v14a2 2 0 0 0 2 2h16v-5"/><path d="M18 12a2 2 0 0 0 0 4h4v-4Z"/></svg>',
    "trending-up": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
    "database": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>',
    "percent": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>',
    "calendar": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "check-circle": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "activity": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "scale": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18"/><path d="m7 21 5-2 5 2"/><path d="M5 7l-3 6a3 3 0 0 0 6 0Z"/><path d="M19 7l-3 6a3 3 0 0 0 6 0Z"/><path d="M5 7h14"/><path d="M12 3 8 7h8Z"/></svg>',
}


def inject_custom_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, .stApp {{
            background-color: {BG} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: {TEXT_PRIMARY};
        }}

        #MainMenu, footer {{ visibility: hidden; }}
        [data-testid="stHeader"] {{ background: transparent; }}
        .block-container {{ padding: 40px 56px 60px 56px; max-width: 1500px; }}

        h1, h2, h3,
        h1 *, h2 *, h3 *,
        [data-testid="stHeadingWithActionElements"] h1,
        [data-testid="stHeadingWithActionElements"] h2,
        [data-testid="stHeadingWithActionElements"] h3,
        [data-testid="stHeadingWithActionElements"] h1 *,
        [data-testid="stHeadingWithActionElements"] h2 *,
        [data-testid="stHeadingWithActionElements"] h3 * {{ color: {TEXT_PRIMARY} !important; }}
        h2, [data-testid="stHeadingWithActionElements"] h2,
        h2 *, [data-testid="stHeadingWithActionElements"] h2 * {{
            font-size: 23px !important;
            font-weight: 700 !important;
            margin-top: 10px;
        }}
        h3, [data-testid="stHeadingWithActionElements"] h3,
        h3 *, [data-testid="stHeadingWithActionElements"] h3 * {{
            font-size: 22px !important;
            font-weight: 600 !important;
        }}
        p, span, label, .stMarkdown {{ color: {TEXT_SECONDARY}; font-size: 15px; }}

        [data-testid="stSidebar"] {{
            background-color: {CARD};
            border-right: 1px solid {BORDER};
        }}
        [data-testid="stSidebar"] .block-container {{ padding: 32px 20px; }}

        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {CARD_SECONDARY};
            border: 1px solid {BORDER} !important;
            border-radius: 16px !important;
            padding: 4px 8px;
            backdrop-filter: blur(16px);
            box-shadow: 0 12px 40px rgba(0,0,0,.25);
            margin-bottom: 14px;
        }}

        .stButton > button {{
            border-radius: 12px;
            border: 1px solid {BORDER};
            background: {CARD_SECONDARY};
            color: {TEXT_PRIMARY};
            font-weight: 600;
            transition: all 200ms ease;
            padding: 0.5rem 1.2rem;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px);
            border-color: {ACCENT};
            box-shadow: 0 8px 24px rgba(79,140,255,.25);
        }}
        .stButton > button[kind="primary"] {{
            background: linear-gradient(90deg, {ACCENT}, {ACCENT_SECONDARY});
            border: none;
            color: #06070A;
        }}

        [data-testid="stExpander"] {{
            background-color: {CARD_SECONDARY};
            border: 1px solid {BORDER};
            border-radius: 16px;
        }}

        [data-testid="stDataFrame"] {{
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid {BORDER};
        }}

        [data-baseweb="slider"] [data-testid="stTickBarMin"],
        [data-baseweb="slider"] [data-testid="stTickBarMax"] {{
            color: {TEXT_MUTED};
        }}

        .hero {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 24px 0 12px 0;
            border-bottom: 1px solid {BORDER};
            margin-bottom: 28px;
            animation: fadeIn 400ms ease;
        }}
        .hero-title {{
            font-size: 48px;
            font-weight: 800;
            line-height: 1.05;
            background: linear-gradient(90deg, {TEXT_PRIMARY}, {TEXT_SECONDARY});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .hero-subtitle {{
            font-size: 15px;
            color: {TEXT_MUTED};
            margin-top: 10px;
            max-width: 560px;
        }}
        .hero-pills {{ display: flex; flex-direction: column; gap: 8px; align-items: flex-end; }}
        .pill {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            color: {TEXT_SECONDARY};
            background: {CARD_SECONDARY};
            border: 1px solid {BORDER};
            padding: 6px 12px;
            border-radius: 999px;
        }}
        .pill-dot {{
            width: 7px; height: 7px; border-radius: 50%;
        }}

        .kpi-card {{
            position: relative;
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 18px;
            padding: 20px 22px;
            backdrop-filter: blur(16px);
            box-shadow: 0 12px 40px rgba(0,0,0,.45);
            transition: transform 200ms ease, box-shadow 200ms ease;
            overflow: hidden;
            animation: slideUp 400ms ease;
            min-height: 132px;
        }}
        .kpi-card::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, {ACCENT}, {ACCENT_SECONDARY});
        }}
        .kpi-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 16px 48px rgba(79,140,255,.18);
            border-color: rgba(79,140,255,.35);
        }}
        .kpi-icon {{ color: {ACCENT}; margin-bottom: 10px; }}
        .kpi-label {{ font-size: 13px; color: {TEXT_MUTED}; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; }}
        .kpi-value {{ font-size: 32px; font-weight: 700; color: {TEXT_PRIMARY}; margin-top: 4px; }}
        .kpi-delta {{ font-size: 13px; font-weight: 600; margin-top: 6px; }}
        .kpi-help {{ font-size: 12px; color: {TEXT_MUTED}; margin-top: 6px; }}

        .hero-chart-title {{ font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY}; }}
        .hero-chart-subtitle {{ font-size: 13px; color: {TEXT_MUTED}; margin-bottom: 12px; }}

        div[class*="st-key-hero_chart"] > div,
        div[class*="st-key-trend_chart"] > div,
        div[class*="st-key-prob_chart"] > div,
        div[class*="st-key-upload_section"] > div {{
            background-color: {CARD_SECONDARY} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 20px !important;
            padding: 28px !important;
            box-shadow: 0 0 0 1px rgba(79,140,255,.08), 0 20px 60px rgba(79,140,255,.14) !important;
            animation: fadeIn 500ms ease;
        }}

        div[class*="st-key-login_card"] {{
            background-color: {CARD} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 20px !important;
            padding: 28px !important;
            box-shadow: 0 0 0 1px rgba(79,140,255,.08), 0 20px 60px rgba(79,140,255,.14) !important;
        }}
        div[class*="st-key-login_card"] [data-testid="stVerticalBlockBorderWrapper"],
        div[class*="st-key-login_card"] [data-testid="stVerticalBlock"] {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin-bottom: 0 !important;
        }}

        div[class*="st-key-recent_tx_card"] > div {{
            background-color: {CARD_SECONDARY} !important;
            border-radius: 20px !important;
            padding: 20px !important;
            border: 2px solid {ACCENT} !important;
            box-shadow: none !important;
        }}

        input, textarea,
        [data-baseweb="input"], [data-baseweb="base-input"],
        [data-baseweb="select"] > div {{
            background-color: {CARD} !important;
            color: {TEXT_PRIMARY} !important;
            border-color: {ACCENT} !important;
        }}
        [data-baseweb="popover"] {{
            background-color: {CARD} !important;
        }}
        [data-baseweb="menu"] {{
            background-color: {CARD} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        [data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] {{
            background-color: {ACCENT} !important;
            color: #FFFFFF !important;
            border-color: {ACCENT} !important;
        }}
        [data-testid="stNumberInputStepUp"] svg, [data-testid="stNumberInputStepDown"] svg {{
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
        }}
        [data-testid="stNumberInputStepUp"]:hover, [data-testid="stNumberInputStepDown"]:hover {{
            background-color: {ACCENT_SECONDARY} !important;
            border-color: {ACCENT_SECONDARY} !important;
        }}

        [data-testid="stTable"] table {{
            background-color: {CARD} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        [data-testid="stTable"] th {{
            background-color: {CARD_SECONDARY} !important;
            color: {TEXT_PRIMARY} !important;
            border-color: {BORDER} !important;
        }}
        [data-testid="stTable"] td {{
            background-color: {CARD} !important;
            color: {TEXT_PRIMARY} !important;
            border-color: {BORDER} !important;
        }}

        hr {{ margin: 14px 0 !important; opacity: .5; }}

        [data-testid="stFileUploaderDropzone"] {{
            background: {CARD_SECONDARY};
            border: 2px dashed rgba(79,140,255,.35) !important;
            border-radius: 16px;
            transition: border-color 200ms ease, box-shadow 200ms ease;
        }}
        [data-testid="stFileUploaderDropzone"]:hover {{
            border-color: {ACCENT} !important;
            box-shadow: 0 8px 24px rgba(79,140,255,.18);
        }}
        [data-testid="stFileUploaderDropzone"] button {{
            border-radius: 12px;
            border: 1px solid {BORDER};
            background: {CARD};
            color: {TEXT_PRIMARY};
            font-weight: 600;
            transition: all 200ms ease;
        }}
        [data-testid="stFileUploaderDropzone"] button:hover {{
            transform: translateY(-2px);
            border-color: {ACCENT};
            box-shadow: 0 8px 24px rgba(79,140,255,.25);
        }}

        .bullet-heading {{ display: flex; align-items: center; gap: 10px; margin: 8px 0 4px 0; }}
        .bullet-dot {{ width: 9px; height: 9px; border-radius: 50%; background: linear-gradient(135deg, {ACCENT}, {ACCENT_SECONDARY}); flex-shrink: 0; }}
        .bullet-text {{ font-size: 22px; font-weight: 600; color: {TEXT_PRIMARY}; }}

        .sidebar-title {{
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .06em;
            color: {TEXT_MUTED};
            margin: 4px 0 16px 4px;
        }}

        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        @keyframes slideUp {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero_header(subtitle: str, pills: list[tuple[str, str, str]]) -> None:
    pills_html = "".join(
        f'<div class="pill"><span class="pill-dot" style="background:{color}"></span>{label}</div>'
        for label, color, _ in pills
    )
    header_html = (
        '<div class="hero">'
        "<div>"
        '<div class="hero-title">Enterprise Financial<br/>Runway Simulator</div>'
        f'<div class="hero-subtitle">{subtitle}</div>'
        "</div>"
        f'<div class="hero-pills">{pills_html}</div>'
        "</div>"
    )
    st.markdown(header_html, unsafe_allow_html=True)


def render_kpi_card(label: str, value: str, delta: float | None = None, icon: str = "wallet", help_text: str | None = None) -> None:
    delta_html = ""
    if delta is not None:
        color = SUCCESS if delta >= 0 else DANGER
        arrow = "&uarr;" if delta >= 0 else "&darr;"
        delta_html = f'<div class="kpi-delta" style="color:{color}">{arrow} {abs(delta):.1f}%</div>'
    help_html = f'<div class="kpi-help">{help_text}</div>' if help_text else ""
    icon_svg = ICONS.get(icon, ICONS["wallet"])
    card_html = (
        '<div class="kpi-card">'
        f'<div class="kpi-icon">{icon_svg}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f"{delta_html}"
        f"{help_html}"
        "</div>"
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_bullet_heading(text: str) -> None:
    st.markdown(
        '<div class="bullet-heading"><span class="bullet-dot"></span>'
        f'<span class="bullet-text">{text}</span></div>',
        unsafe_allow_html=True,
    )


def register_altair_theme() -> None:
    def _premium_dark_theme():
        return {
            "config": {
                "background": "transparent",
                "view": {"stroke": "transparent", "continuousHeight": 380},
                "axis": {
                    "domainColor": CHART_DOMAIN,
                    "gridColor": CHART_GRID,
                    "tickColor": CHART_DOMAIN,
                    "labelColor": TEXT_SECONDARY,
                    "titleColor": TEXT_SECONDARY,
                    "labelFontSize": 11,
                    "titleFontSize": 12,
                    "labelFont": "Inter",
                    "titleFont": "Inter",
                },
                "legend": {
                    "labelColor": TEXT_SECONDARY,
                    "titleColor": TEXT_PRIMARY,
                    "labelFont": "Inter",
                    "titleFont": "Inter",
                },
                "range": {
                    "category": [ACCENT, ACCENT_SECONDARY, SUCCESS, WARNING, DANGER],
                },
                "line": {"color": ACCENT, "strokeWidth": 2.5, "interpolate": "monotone"},
                "area": {"color": ACCENT, "opacity": 0.25, "interpolate": "monotone"},
                "bar": {"color": ACCENT, "cornerRadiusEnd": 4},
                "point": {"color": ACCENT},
            }
        }

    alt.themes.register("premium_dark", _premium_dark_theme)
    alt.themes.enable("premium_dark")
