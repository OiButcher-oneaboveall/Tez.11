
import plotly.figure_factory as ff
import plotly.graph_objects as go
import folium
from folium import Tooltip, PolyLine, Marker, Icon
from datetime import datetime

city_coords = {
    "Rafineri": [41.0351, 28.7663],
    "Gürpınar": [40.9946, 28.5764],
    "Yenikapı": [41.0030, 28.9497],
    "Selimiye": [41.0054, 29.0275],
    "İçerenköy": [40.9845, 29.0936],
    "Tophane": [41.0273, 28.9768],
    "Alibeyköy": [41.0662, 28.9314],
    "İstinye": [41.1099, 29.0570]
}

def plot_gantt(log):
    base_date = datetime(2024, 1, 1)
    tasks = []
    for entry in log:
        start_time = datetime.strptime(entry["arrival"], "%H:%M")
        end_time = datetime.strptime(entry["departure"], "%H:%M")
        start_dt = base_date.replace(hour=start_time.hour, minute=start_time.minute)
        end_dt = base_date.replace(hour=end_time.hour, minute=end_time.minute)
        tasks.append(dict(Task=f"{entry['from']}→{entry['to']}", Start=start_dt, Finish=end_dt))
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
        to_city = city_names[i + 1]
        coord1 = city_coords.get(from_city)
        coord2 = city_coords.get(to_city)
        if coord1 and coord2:
            duration = ""
            if log:
                for entry in log:
                    if entry["from"] == from_city and entry["to"] == to_city:
                        start = entry["arrival"]
                        end = entry["departure"]
                        sh, sm = map(int, start.split(":"))
                        eh, em = map(int, end.split(":"))
                        duration = f"{(eh * 60 + em) - (sh * 60 + sm)} dk"
                        break
            label = f"{from_city} → {to_city}<br>{duration}" if duration else f"{from_city} → {to_city}"
            folium.PolyLine([coord1, coord2], color="red", weight=5,
                            tooltip=Tooltip(label, sticky=True)).add_to(m)
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
