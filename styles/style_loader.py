import streamlit as st
import base64
import os

SVG_BACKGROUND = """
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
  <style>
    .node  { fill: #802B45; opacity: 0.04; }
    .edge  { stroke: #802B45; stroke-width: 1.5; opacity: 0.03; stroke-dasharray: 4 4; }
    .shield{ fill: #802B45; opacity: 0.02; }
  </style>
  <g transform="translate(40, 120)">
    <circle cx="100" cy="100" r="35" class="node"/>
    <circle cx="240" cy="50"  r="20" class="node"/>
    <circle cx="220" cy="200" r="25" class="node"/>
    <circle cx="80"  cy="320" r="22" class="node"/>
    <line x1="100" y1="100" x2="240" y2="50"  class="edge"/>
    <line x1="100" y1="100" x2="220" y2="200" class="edge"/>
    <line x1="100" y1="100" x2="80"  y2="320" class="edge"/>
  </g>
  <g transform="translate(900, 80)">
    <path d="M50,10 L150,10 L150,110 L100,160 L50,110 Z" class="shield"/>
    <circle cx="0" cy="80" r="30" class="node"/>
    <line x1="0" y1="80" x2="50" y2="60" class="edge"/>
  </g>
</svg>
"""


def load_styles():
    """Inject global CSS + SVG background into the Streamlit app."""
    # Read the CSS file relative to this file's location
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    with open(css_path, "r") as f:
        css = f.read()

    bg_b64 = base64.b64encode(SVG_BACKGROUND.encode()).decode()

    # Inject background image URL into the .stApp rule dynamically
    bg_injection = f"""
    .stApp {{
        background-image: url('data:image/svg+xml;base64,{bg_b64}');
    }}
    """

    st.markdown(f"<style>{css}\n{bg_injection}</style>", unsafe_allow_html=True)
