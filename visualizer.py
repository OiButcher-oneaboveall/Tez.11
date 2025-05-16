
import plotly.figure_factory as ff
import plotly.graph_objects as go
import folium

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
    tasks = []
    for i, entry in enumerate(log):
        start = entry["arrival"]
        end = entry["departure"]
        tasks.append(dict(Task=f"{entry['from']}→{entry['to']}", Start=start, Finish=end))
    fig = ff.create_gantt(tasks, index_col='Task', show_colorbar=True, group_tasks=True)
    return fig

def plot_folium_route(city_names):
    start_coord = city_coords.get("Rafineri", [41.015, 28.979])
    m = folium.Map(location=start_coord, zoom_start=11)
    for city in city_names:
        coord = city_coords.get(city)
        if coord:
            folium.Marker(location=coord, tooltip=city, icon=folium.Icon(color="blue")).add_to(m)
    path = [city_coords[city] for city in city_names if city in city_coords]
    folium.PolyLine(path, color="red", weight=5).add_to(m)
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
