
import streamlit as st
from optimizer import run_ga
from visualizer import plot_gantt, plot_folium_route
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Rota Optimizasyonu")

st.markdown("<h1 style='color: white;'>🚛 Rota Optimizasyon Arayüzü</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("Parametreler")
    pop_size = st.slider("Popülasyon Büyüklüğü", 10, 5000, 100, step=10)
    generations = st.slider("Nesil Sayısı", 10, 2500, 200, step=10)
    max_risk = st.slider("Maksimum Risk", 0.0, 1.0, 0.3, step=0.01)
    hedef = st.selectbox(
        "Amaç Fonksiyonu",
        ["Minimum Süre", "Minimum Mesafe", "Minimum Risk", "Maksimum Ortalama Hız"]
    )

if "sonuc" not in st.session_state:
    st.session_state.sonuc = None

if st.button("🚀 Optimizasyonu Başlat"):
    with st.spinner("Genetik algoritma çalışıyor..."):
        route, dist, time, risk, log, avg_speed = run_ga(pop_size, generations, max_risk, hedef)
        st.session_state.sonuc = {
            "route": route, "dist": dist, "time": time,
            "risk": risk, "log": log, "avg_speed": avg_speed
        }
    st.success("✅ Optimizasyon tamamlandı!")

if st.session_state.sonuc:
    son = st.session_state.sonuc
    st.subheader("📊 Optimizasyon Sonuçları")
    st.write(f"**Toplam Mesafe:** {son['dist']:.2f} km")
    st.write(f"**Toplam Süre:** {son['time']:.2f} dk")
    st.write(f"**Toplam Risk:** {son['risk']:.4f}")
    st.write(f"**Ortalama Hız:** {son['avg_speed']:.2f} km/s")

    st.subheader("🗺️ Rota Haritası")
    fmap = plot_folium_route(son["route"], son["log"])
    fmap.save("map.html")
    with open("map.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=600)

    st.subheader("📅 Zaman Çizelgesi (Gantt Grafiği)")
    fig = plot_gantt(son["log"])
    st.plotly_chart(fig, use_container_width=True)
