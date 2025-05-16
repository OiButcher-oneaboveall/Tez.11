
def plot_gantt(log):
    from datetime import datetime, timedelta
    import plotly.graph_objects as go

    base_date = datetime(2024, 1, 1)
    colors = {
        "Yol": "rgb(31, 119, 180)",
        "Bekleme": "rgb(255, 127, 14)",
        "Servis": "rgb(44, 160, 44)"
    }

    bars = []
    y_labels = []
    for idx, entry in enumerate(log):
        try:
            start_dt = datetime.strptime(entry["departure"][:5], "%H:%M")
            end_dt = datetime.strptime(entry["arrival"][:5], "%H:%M")

            if start_dt < end_dt:
                bars.append(dict(
                    Task=f"{entry['from']}→{entry['to']} (Yol)",
                    Start=start_dt,
                    Finish=end_dt,
                    Color=colors["Yol"]
                ))
                y_labels.append(f"{entry['from']}→{entry['to']} (Yol)")

            wait_min = entry.get("wait", 0)
            if wait_min > 0:
                wait_start = end_dt
                wait_end = wait_start + timedelta(minutes=wait_min)
                if wait_start < wait_end:
                    bars.append(dict(
                        Task=f"{entry['to']} (Bekleme)",
                        Start=wait_start,
                        Finish=wait_end,
                        Color=colors["Bekleme"]
                    ))
                    y_labels.append(f"{entry['to']} (Bekleme)")
                end_dt = wait_end

            service_min = entry.get("service", 0)
            if service_min > 0:
                service_start = end_dt
                service_end = service_start + timedelta(minutes=service_min)
                if service_start < service_end:
                    bars.append(dict(
                        Task=f"{entry['to']} (Servis)",
                        Start=service_start,
                        Finish=service_end,
                        Color=colors["Servis"]
                    ))
                    y_labels.append(f"{entry['to']} (Servis)")

        except Exception as e:
            print(f"Gantt log hatası: {e}")

    fig = go.Figure()
    for bar in bars:
        duration = (bar["Finish"] - bar["Start"]).total_seconds() / 60
        fig.add_trace(go.Bar(
            x=[duration],
            y=[bar["Task"]],
            base=bar["Start"],
            orientation='h',
            marker=dict(color=bar["Color"]),
            hovertemplate=f"{bar['Task']}<br>%{{base|%H:%M}} - %{{x|.0f}} dk<extra></extra>"
        ))

    fig.update_layout(
        title="Zaman Çizelgesi (Gantt Şeması)",
        xaxis=dict(title="Zaman", type="date"),
        yaxis=dict(title="Görev", automargin=True),
        height=600,
        margin=dict(l=150, r=20, t=40, b=40)
    )

    return fig
