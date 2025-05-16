
import streamlit as st
from streamlit_option_menu import option_menu
from optimizer import run_ga
from visualizer import plot_gantt, plot_folium_route
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Rota Optimizasyonu", page_icon="🧭")

with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/FFFFFF/tanker-truck.png", width=80)
    st.title("Parametreler")
    pop_size = st.slider("Popülasyon Büyüklüğü", 10, 5000, 100, step=10)
    generations = st.slider("Nesil Sayısı", 10, 2500, 200, step=10)
    max_risk = st.slider("Maksimum Risk", 0.0, 1.0, 0.3, step=0.01)
    hedef = st.selectbox(
        "Amaç Fonksiyonu",
        ["Minimum Süre", "Minimum Mesafe", "Minimum Risk", "Maksimum Ortalama Hız"]
    )

selected = option_menu(
    menu_title=None,
    options=["🧮 Optimizasyon", "🗺️ Harita", "📊 Zaman Çizelgesi"],
    icons=["gear", "map", "bar-chart"],
    orientation="horizontal"
)

if "sonuc" not in st.session_state:
    st.session_state.sonuc = None

if selected == "🧮 Optimizasyon":
    st.title("🚛 Akaryakıt Rota Optimizasyonu")
    if st.button("🚀 Hesapla"):
        with st.spinner("Genetik algoritma çalışıyor..."):
            route, dist, time, risk, log, avg_speed = run_ga(pop_size, generations, max_risk, hedef)
            st.session_state.sonuc = {
                "route": route, "dist": dist, "time": time,
                "risk": risk, "log": log, "avg_speed": avg_speed
            }
        st.success("✅ Optimizasyon tamamlandı!")

    if st.session_state.sonuc:
        son = st.session_state.sonuc
        st.metric("📍 Toplam Mesafe (km)", f"{son['dist']:.2f}")
        st.metric("⏱️ Toplam Süre (dk)", f"{son['time']:.2f}")
        st.metric("☢️ Toplam Risk", f"{son['risk']:.4f}")
        st.metric("🚀 Ortalama Hız (km/s)", f"{son['avg_speed']:.2f}")

elif selected == "🗺️ Harita":
    st.title("🗺️ Gerçek Yol Haritası")
    if st.session_state.sonuc:
        fmap = plot_folium_route(st.session_state.sonuc["route"], st.session_state.sonuc["log"])
        fmap.save("map.html")
        with open("map.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=600)
    else:
        st.warning("Lütfen önce optimizasyonu çalıştırın.")

elif selected == "📊 Zaman Çizelgesi":
    st.title("📊 Gantt Grafiği")
    if st.session_state.sonuc:
        fig = plot_gantt(st.session_state.sonuc["log"])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Lütfen önce optimizasyonu çalıştırın.")
