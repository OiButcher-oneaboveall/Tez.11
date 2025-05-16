
import streamlit as st
from optimizer import run_ga
from visualizer import plot_gantt, plot_folium_route
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Tez Rota Arayüzü")
st.markdown("<h1 style='color: white;'>🚛 Akaryakıt Dağıtım Optimizasyonu</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Parametreler")
    pop_size = st.slider("Popülasyon Büyüklüğü", 10, 5000, 100, step=10)
    generations = st.slider("Nesil Sayısı", 10, 2500, 200, step=10)
    max_risk = st.slider("Maksimum Risk", 0.0, 1.0, 0.3, step=0.01)
    hedef = st.selectbox(
        "Amaç Fonksiyonu",
        ["Minimum Süre", "Minimum Mesafe", "Minimum Risk", "Maksimum Ortalama Hız"]
    )

if st.button("🚀 Optimizasyonu Başlat"):
    with st.spinner("Genetik algoritma çalışıyor..."):
        route, dist, time, risk, log, avg_speed = run_ga(pop_size, generations, max_risk, hedef)

    st.success("✅ En iyi rota bulundu!")
    st.write(f"**Toplam Mesafe:** {dist:.2f} km")
    st.write(f"**Toplam Süre:** {time:.2f} dk")
    st.write(f"**Toplam Risk:** {risk:.4f}")
    st.write(f"**Ortalama Hız:** {avg_speed:.2f} km/s")

    st.subheader("🗺️ Rota Haritası")
    fmap = plot_folium_route(route, log)
    fmap.save("map.html")
    with open("map.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=500)

    st.subheader("📊 Gantt Grafiği")
    fig = plot_gantt(log)
    st.plotly_chart(fig, use_container_width=True)
