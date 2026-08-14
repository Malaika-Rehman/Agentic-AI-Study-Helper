def progress_ring(pct: int, color: str, size: int = 75) -> str:
    """Returns an SVG progress ring as an HTML string."""
    r = 38
    circ = 2 * 3.14159 * r
    offset = circ * (1 - pct / 100)
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="{r}" fill="none" stroke="#F4ECEF" stroke-width="9"/>
      <circle cx="50" cy="50" r="{r}" fill="none" stroke="{color}" stroke-width="9"
        stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}"
        stroke-linecap="round" transform="rotate(-90 50 50)"/>
      <text x="50" y="56" text-anchor="middle" font-size="17" font-weight="700"
        fill="{color}" font-family="DM Sans">{pct}%</text>
    </svg>"""
