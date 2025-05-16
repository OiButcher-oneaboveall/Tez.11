
def plot_gantt(log):
    import plotly.graph_objects as go

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

            # Yolculuk
            if start_minute < end_minute:
                bars.append(dict(
                    Task=f"{entry['from']}→{entry['to']} (Yol)",
                    Start=start_minute,
                    Duration=end_minute - start_minute,
                    Color=colors["Yol"]
                ))

            # Servis süresi (rafineri hariç)
            if entry["to"] != "Rafineri":
                service_min = entry.get("service", 0)
                if service_min > 0:
                    bars.append(dict(
                        Task=f"{entry['to']} (Servis)",
                        Start=end_minute,
                        Duration=service_min,
                        Color=colors["Servis"]
                    ))
                    end_minute += service_min

            # Bekleme süresi (eğer çakışmıyorsa)
            wait_min = entry.get("wait", 0)
            if wait_min > 0:
                next_departure_minute = None
                if i + 1 < len(log):
                    next_dep_h, next_dep_m = map(int, log[i + 1]["departure"][:5].split(":"))
                    next_departure_minute = next_dep_h * 60 + next_dep_m

                if not next_departure_minute or (end_minute + wait_min <= next_departure_minute):
                    bars.append(dict(
                        Task=f"{entry['to']} (Bekleme)",
                        Start=end_minute,
                        Duration=wait_min,
                        Color=colors["Bekleme"]
                    ))
                    end_minute += wait_min

        except Exception as e:
            print("Zaman çizelgesi hatası:", e)

    def to_hour_min(minute):
        return f"{minute//60:02d}:{minute%60:02d}"

    fig = go.Figure()
    for bar in bars:
        fig.add_trace(go.Bar(
            x=[bar["Duration"]],
            y=[bar["Task"]],
            base=bar["Start"],
            orientation="h",
            marker=dict(color=bar["Color"]),
            hovertemplate=f"{bar['Task']}<br>Başlangıç: {to_hour_min(bar['Start'])}<br>Süre: {{x}} dk<extra></extra>"
        ))

    fig.update_layout(
        title="Zaman Çizelgesi (Yol → Servis → Bekleme / Çakışmasız)",
        xaxis=dict(
            title="Zaman (saat:dakika)",
            tickmode="array",
            tickvals=list(range(360, 1100, 30)),
            ticktext=[to_hour_min(t) for t in range(360, 1100, 30)]
        ),
        yaxis=dict(title="Görev", automargin=True),
        height=700,
        margin=dict(l=150, r=20, t=40, b=40)
    )
    return fig
