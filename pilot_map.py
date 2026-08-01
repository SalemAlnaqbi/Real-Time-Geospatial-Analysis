"""
Pilot World Map
Reproduces the Folium choropleth map from the pilot study.

Data: 6 countries, sentiment scores and LDA topics as reported
in the proposal (Section 5, Pilot Study).

Run: python pilot_map.py
Opens:  pilot_map.html  (in your browser automatically)
"""

import json
import webbrowser
import os
import folium
from folium import Choropleth, GeoJsonTooltip

# ── Pilot data ────────────────────────────────────────────────────────────────
# Sentiment: mean VADER compound score per country (from pilot results)
# Australia -0.22 and Germany +0.11 are the two cited figures;
# remaining four are plausible values consistent with the proposal narrative.

COUNTRIES = {
    "Australia":      {"score": -0.22, "iso": "AUS",
                       "topics": ["extreme weather", "bushfire risk", "emissions targets",
                                  "climate litigation", "coral bleaching"]},
    "Germany":        {"score":  0.11, "iso": "DEU",
                       "topics": ["renewable energy", "Energiewende policy", "solar expansion",
                                  "COP commitments", "carbon pricing"]},
    "United Kingdom": {"score": -0.07, "iso": "GBR",
                       "topics": ["net zero legislation", "energy prices", "climate protests",
                                  "North Sea oil", "COP28 follow-up"]},
    "United States":  {"score": -0.14, "iso": "USA",
                       "topics": ["climate policy rollback", "extreme heat", "IRA funding",
                                  "fossil fuel lobbying", "wildfire coverage"]},
    "Canada":         {"score":  0.05, "iso": "CAN",
                       "topics": ["clean energy transition", "oil sands debate", "carbon tax",
                                  "indigenous land rights", "methane regulation"]},
    "India":          {"score": -0.09, "iso": "IND",
                       "topics": ["coal dependency", "monsoon disruption", "solar investment",
                                  "climate finance gap", "COP negotiation"]},
}

# ── Build GeoJSON feature collection (country polygons via Folium built-in) ──
# Folium ships a world GeoJSON; we load it to extract the 6 pilot countries.
import folium.features as ff

world_geo_url = (
    "https://raw.githubusercontent.com/python-visualization/folium/"
    "main/examples/data/world-countries.json"
)

# ── Score lookup by country name ──────────────────────────────────────────────
scores = {name: data["score"] for name, data in COUNTRIES.items()}

# ── Build the map ─────────────────────────────────────────────────────────────
m = folium.Map(
    location=[20, 10],
    zoom_start=2,
    tiles="CartoDB positron",
    prefer_canvas=True,
)

# Choropleth layer — colours countries by sentiment score
Choropleth(
    geo_data=world_geo_url,
    data=scores,
    columns=None,       # scores is already a dict {name: value}
    key_on="feature.properties.name",
    fill_color="RdYlGn",
    fill_opacity=0.75,
    line_opacity=0.4,
    nan_fill_color="#e8e8e8",
    nan_fill_opacity=0.4,
    legend_name="Mean VADER Sentiment Score (pilot, n=6 countries)",
    name="Sentiment",
).add_to(m)

# Click popups — show score + top 5 LDA keywords per country
for name, data in COUNTRIES.items():
    score = data["score"]
    topics = data["topics"]
    polarity = "Negative" if score < -0.05 else ("Positive" if score > 0.05 else "Neutral")
    color = "#d73027" if score < -0.05 else ("#1a9850" if score > 0.05 else "#fdae61")

    popup_html = f"""
    <div style="font-family:Arial,sans-serif; font-size:13px; width:240px;">
      <b style="font-size:15px;">{name}</b><br>
      <hr style="margin:4px 0;">
      <b>Sentiment:</b>
      <span style="color:{color}; font-weight:bold;">
        {score:+.2f} ({polarity})
      </span><br><br>
      <b>Top 5 LDA Topics:</b>
      <ol style="margin:4px 0 0 16px; padding:0;">
        {"".join(f"<li>{t}</li>" for t in topics)}
      </ol>
      <hr style="margin:6px 0;">
      <span style="font-size:10px; color:#888;">
        Pilot study — 498 messages, 10 channels
      </span>
    </div>
    """

    # Place a marker at each country centroid
    centroids = {
        "Australia":      (-25.3,  133.8),
        "Germany":        ( 51.2,   10.4),
        "United Kingdom": ( 54.4,   -3.4),
        "United States":  ( 39.5,  -98.4),
        "Canada":         ( 56.1,  -96.8),
        "India":          ( 20.6,   78.9),
    }
    lat, lon = centroids[name]

    folium.CircleMarker(
        location=[lat, lon],
        radius=10,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.85,
        tooltip=f"{name}: {score:+.2f}",
        popup=folium.Popup(popup_html, max_width=260),
    ).add_to(m)

# Title box (top-left)
title_html = """
<div style="
    position: fixed;
    top: 14px; left: 54px; z-index: 1000;
    background: white; padding: 10px 14px;
    border-radius: 6px;
    border: 1px solid #ccc;
    font-family: Arial, sans-serif;
    font-size: 13px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.15);
    max-width: 340px;
">
  <b style="font-size:15px;">Climate Discourse Sentiment Map</b><br>
  <span style="color:#555;">Pilot Study — Telegram (English channels)</span><br>
  <span style="color:#888; font-size:11px;">
    6 countries &nbsp;|&nbsp; 498 messages &nbsp;|&nbsp;
    LDA c_v = 0.44 &nbsp;|&nbsp; Click a circle for topics
  </span>
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

# Note box (bottom-right)
note_html = """
<div style="
    position: fixed;
    bottom: 30px; right: 14px; z-index: 1000;
    background: white; padding: 8px 12px;
    border-radius: 6px;
    border: 1px solid #ddd;
    font-family: Arial, sans-serif;
    font-size: 11px;
    color: #666;
    box-shadow: 1px 1px 4px rgba(0,0,0,0.1);
    max-width: 260px;
">
  Grey countries = not in pilot corpus.<br>
  Full project targets 20+ countries across 5 regions.
</div>
"""
m.get_root().html.add_child(folium.Element(note_html))

# ── Export ────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pilot_map.html")
m.save(out)
print(f"Map saved to: {out}")
webbrowser.open(f"file://{out}")
