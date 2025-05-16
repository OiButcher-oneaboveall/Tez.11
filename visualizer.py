import plotly.graph_objects as go
import folium
from folium import Marker, Icon, Tooltip, DivIcon, PolyLine
from datetime import datetime
import openrouteservice

city_coords = {
    "Rafineri": [41.0343, 28.7662],
    "Gürpınar": [40.9802, 28.6131],
    "Yenikapı": [41.0048, 28.9497],
    "Selimiye": [41.0054, 29.0240],
    "İçerenköy": [40.9854, 29.0933],
    "Tophane": [41.0292, 28.9768],
    "Alibeyköy": [41.0696, 28.9366],
    "İstinye": [41.1099, 29.0570]
}

ors_client = openrouteservice.Client(key="5b3ce3597851110001cf62486f7204b3263d422c812e8c793740ded5")

def plot_gantt(log):
    colors = {
        "Yol": "#1f77b4",
        "Bekleme": "#ff7f0e",
        "Servis": "#2ca02c"
    }
    bars = []
    for i, entry in enumerate(log):
        try:
            dep_hour, dep_min = map(int, entry["departure"][:5].split(":"))
            arr_hour, arr_min = map(int, entry["arrival"][:5].split(":"))
            start_minute = dep_hour * 60 + dep_min
            end_minute = arr_hour * 60 + arr_min
            if start_minute < end_minute:
                bars.append(dict(Task=f"{entry['from']}→{entry['to']} (Yol)", Start=start_minute, Duration=end_minute - start_minute, Color=colors["Yol"]))
            if entry["to"] != "Rafineri":
                service_min = entry.get("service", 0)
                if service_min > 0:
                    bars.append(dict(Task=f"{entry['to']} (Servis)", Start=end_minute, Duration=service_min, Color=colors["Servis"]))
                    end_minute += service_min
            wait_min = entry.get("wait", 0)
            if wait_min > 0:
                next_departure_minute = None
                if i + 1 < len(log):
                    next_dep_h, next_dep_m = map(int, log[i + 1]["departure"][:5].split(":"))
                    next_departure_minute = next_dep_h * 60 + next_dep_m
                if not next_departure_minute or (end_minute + wait_min <= next_departure_minute):
                    bars.append(dict(Task=f"{entry['to']} (Bekleme)", Start=end_minute, Duration=wait_min, Color=colors["Bekleme"]))
                    end_minute += wait_min
        except Exception as e:
            print("Zaman çizelgesi hatası:", e)

    def to_hour_min(minute):
        return f"{minute//60:02d}:{minute%60:02d}"

    fig = go.Figure()
    for bar in bars:
        fig.add_trace(go.Bar(x=[bar["Duration"]], y=[bar["Task"]], base=bar["Start"], orientation="h",
                             marker=dict(color=bar["Color"]),
                             hovertemplate=f"{bar['Task']}<br>Başlangıç: {to_hour_min(bar['Start'])}<br>Süre: {{x}} dk<extra></extra>"))
    fig.update_layout(title="Zaman Çizelgesi (Yol → Servis → Bekleme / Çakışmasız)",
                      xaxis=dict(title="Zaman (saat:dakika)", tickmode="array",
                                 tickvals=list(range(360, 1100, 30)),
                                 ticktext=[to_hour_min(t) for t in range(360, 1100, 30)]),
                      yaxis=dict(title="Görev", automargin=True), height=700,
                      margin=dict(l=150, r=20, t=40, b=40))
    return fig

def plot_folium_route(city_names, log=None):
    m = folium.Map(location=[41.03, 28.96], zoom_start=11)
    for idx, city in enumerate(city_names):
        coord = city_coords.get(city)
        if coord:
            label = f"{idx+1}. {city}"
            Marker(location=coord, tooltip=label, icon=Icon(color="blue")).add_to(m)

    for i in range(len(city_names) - 1):
        from_city = city_names[i]
        to_city = city_names[i+1]
        coord1 = city_coords[from_city]
        coord2 = city_coords[to_city]
        try:
            route = ors_client.directions(
                coordinates=[coord1[::-1], coord2[::-1]],
                profile='driving-car',
                format='geojson'
            )
            tooltip = f"{from_city} → {to_city}"
            time_text = ""
            if log:
                for entry in log:
                    if entry["from"] == from_city and entry["to"] == to_city:
                        time_text = f"{entry['departure']}–{entry['arrival']}"
                        break
            folium.GeoJson(route, tooltip=f"{tooltip}<br>{time_text}").add_to(m)
            mid_idx = len(route["features"][0]["geometry"]["coordinates"]) // 2
            lon, lat = route["features"][0]["geometry"]["coordinates"][mid_idx]
            folium.map.Marker(
                [lat, lon],
                icon=DivIcon(icon_size=(150,36), icon_anchor=(0,0),
                    html=f'<div style="font-size: 10pt; color: black; background: white; padding: 2px; border-radius: 3px;">{time_text}</div>')
            ).add_to(m)
        except Exception:
            PolyLine([coord1, coord2], color="red", weight=5,
                     tooltip=Tooltip(f"{from_city} → {to_city}")).add_to(m)
    return m

def plot_scenario_comparison(data):
    fig = go.Figure()
    names = [d['name'] for d in data]
    fig.add_trace(go.Bar(name="Mesafe", x=names, y=[d['dist'] for d in data]))
    fig.add_trace(go.Bar(name="Süre", x=names, y=[d['time'] for d in data]))
    fig.add_trace(go.Bar(name="Risk", x=names, y=[d['risk'] for d in data]))
    fig.add_trace(go.Bar(name="Hız", x=names, y=[d.get('avg_speed', 0) for d in data]))
    fig.update_layout(barmode='group')
    return fig

def plot_emission_energy_comparison(data):
    fig = go.Figure()
    names = [d['name'] for d in data]
    emissions = [round(d['dist'] * 0.2, 2) for d in data]
    energy = [round(d['dist'] * 0.25, 2) for d in data]
    fig.add_trace(go.Bar(name="CO₂ (kg)", x=names, y=emissions))
    fig.add_trace(go.Bar(name="Enerji (kWh)", x=names, y=energy))
    fig.update_layout(barmode='group')
    return fig
