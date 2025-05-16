
import streamlit as st
from optimizer import run_ga
from visualizer import (
    plot_gantt,
    plot_folium_route,
    plot_scenario_comparison,
    plot_emission_energy_comparison
)
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Rota Optimizasyonu", page_icon="🚛")

if "sonuc" not in st.session_state:
    st.session_state.sonuc = None
if "senaryolar" not in st.session_state:
    st.session_state.senaryolar = []

st.title("🚛 Rota Optimizasyon Uygulaması")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("### Parametre Girişi")
with col2:
    st.markdown("### " + " ")

with st.form("opt_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pop_size = st.slider("Popülasyon Büyüklüğü", 10, 5000, 100, step=10)
    with col2:
        generations = st.slider("Nesil Sayısı", 10, 2500, 200, step=10)
    with col3:
        max_risk = st.slider("Maksimum Risk", 0.0, 15.0, 0.3, step=0.1)

    col4, col5 = st.columns([3, 1])
    with col4:
        hedef = st.selectbox("Amaç Fonksiyonu", [
            "Minimum Süre", "Minimum Mesafe", "Minimum Risk", "Maksimum Ortalama Hız"
        ])
    with col5:
        isim = st.text_input("Senaryo İsmi", value=f"Senaryo-{len(st.session_state.senaryolar)+1}")

    hesapla = st.form_submit_button("🚀 Hesapla ve Kaydet")

if hesapla:
    with st.spinner("Genetik algoritma çalışıyor..."):
        route, dist, time, risk, log, avg_speed = run_ga(pop_size, generations, max_risk, hedef)
        st.session_state.sonuc = {
            "name": isim,
            "route": route,
            "dist": dist,
            "time": time,
            "risk": risk,
            "log": log,
            "avg_speed": avg_speed
        }
        st.session_state.senaryolar.append(st.session_state.sonuc)
    st.success("✅ Senaryo başarıyla hesaplandı ve kaydedildi!")

if st.session_state.sonuc:
    son = st.session_state.sonuc
    st.subheader("📊 Optimizasyon Sonuçları")
    st.write(f"**Senaryo:** {son['name']}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam Mesafe (km)", f"{son['dist']:.2f}")
    col2.metric("Toplam Süre (dk)", f"{son['time']:.2f}")
    col3.metric("Toplam Risk", f"{son['risk']:.4f}")
    col4.metric("Ortalama Hız (km/s)", f"{son['avg_speed']:.2f}")

    st.subheader("🗺️ Rota Haritası")
    fmap = plot_folium_route(son["route"], son["log"])
    fmap.save("map.html")
    with open("map.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=600)

    st.subheader("📅 Zaman Çizelgesi (Gantt Grafiği)")
    fig = plot_gantt(son["log"])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Senaryo Karşılaştırması")
    if len(st.session_state.senaryolar) > 1:
        fig2 = plot_scenario_comparison(st.session_state.senaryolar)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Karşılaştırma için en az 2 senaryo hesaplanmalı.")

    st.subheader("🌍 Karbon ve Enerji Analizi")
    fig3 = plot_emission_energy_comparison(st.session_state.senaryolar)
    st.plotly_chart(fig3, use_container_width=True)
