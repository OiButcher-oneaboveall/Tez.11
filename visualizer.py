
import plotly.figure_factory as ff
import plotly.graph_objects as go
import folium
from folium import Tooltip, PolyLine, Marker, Icon
from datetime import datetime, timedelta
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

ors_client = openrouteservice.Client(key="your-api-key")  # <- Buraya kendi API key'ini gir


import plotly.figure_factory as ff
from datetime import datetime, timedelta

def plot_gantt(log):
    base_date = datetime(2024, 1, 1)
    tasks = []
    for entry in log:
        start_dt = datetime.strptime(entry["departure"][:5], "%H:%M").replace(year=2024, month=1, day=1)
        end_dt = datetime.strptime(entry["arrival"][:5], "%H:%M").replace(year=2024, month=1, day=1)
        if start_dt < end_dt:
            tasks.append(dict(Task=f"{entry['from']}→{entry['to']} (Yol)", Start=start_dt, Finish=end_dt))
        wait_min = entry.get("wait", 0)
        if wait_min > 0:
            wait_start = end_dt
            wait_end = wait_start + timedelta(minutes=wait_min)
            tasks.append(dict(Task=f"{entry['to']} (Bekleme)", Start=wait_start, Finish=wait_end))
            end_dt = wait_end
        service_min = entry.get("service", 0)
        if service_min > 0:
            service_start = end_dt
            service_end = service_start + timedelta(minutes=service_min)
            tasks.append(dict(Task=f"{entry['to']} (Servis)", Start=service_start, Finish=service_end))
    fig = ff.create_gantt(tasks, index_col='Task', show_colorbar=True, group_tasks=True,
                          showgrid_x=True, showgrid_y=True)
    return fig
def plot_folium_route(city_names, log=None):
    start_coord = city_coords.get("Rafineri", [41.015, 28.979])
    m = folium.Map(location=start_coord, zoom_start=11)

    for city in city_names:
        coord = city_coords.get(city)
        if coord:
            folium.Marker(location=coord, tooltip=city, icon=folium.Icon(color="blue")).add_to(m)

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
            if log:
                for entry in log:
                    if entry["from"] == from_city and entry["to"] == to_city:
                        sh, sm = map(int, entry["departure"].split(":")[:2])
                        eh, em = map(int, entry["arrival"].split(":")[:2])
                        duration = (eh * 60 + em) - (sh * 60 + sm)
                        tooltip += f"<br>{duration} dk"
                        break
            folium.GeoJson(route, name="route", tooltip=tooltip).add_to(m)

        except Exception:
            folium.PolyLine([coord1, coord2], color="red", weight=5,
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
