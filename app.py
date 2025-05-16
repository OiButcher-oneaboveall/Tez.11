
import streamlit as st
from streamlit_option_menu import option_menu
from optimizer import run_ga
from visualizer import (
    plot_gantt,
    plot_folium_route,
    plot_scenario_comparison,
    plot_emission_energy_comparison
)
import streamlit.components.v1 as components
import json

st.set_page_config(layout="wide", page_title="Rota Optimizasyonu", page_icon="🚛")

if "sonuc" not in st.session_state:
    st.session_state.sonuc = None
if "senaryolar" not in st.session_state:
    st.session_state.senaryolar = []

with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/FFFFFF/gas-pump.png", width=60)
    st.title("Parametreler")

    pop_size = st.slider("Popülasyon Büyüklüğü", 10, 5000, 100, step=10)
    generations = st.slider("Nesil Sayısı", 10, 2500, 200, step=10)
    max_risk = st.slider("Maksimum Risk", 0.0, 15.0, 0.3, step=0.1)
    hedef = st.selectbox("Amaç Fonksiyonu", ["Minimum Süre", "Minimum Mesafe", "Minimum Risk", "Maksimum Ortalama Hız"])
    isim = st.text_input("Senaryo İsmi", value=f"Senaryo-{len(st.session_state.senaryolar)+1}")
    hesapla = st.button("🚀 Hesapla ve Kaydet")

    st.markdown("---")
    if st.session_state.sonuc:
        st.download_button(
            "📤 Senaryoyu Dışa Aktar (JSON)",
            data=json.dumps(st.session_state.sonuc, indent=2),
            file_name=f"{st.session_state.sonuc['name']}.json",
            mime="application/json"
        )
    uploaded_file = st.file_uploader("📥 Senaryo Yükle (.json)", type=["json"])
    if uploaded_file is not None:
        try:
            uploaded_data = json.load(uploaded_file)
            st.session_state.sonuc = uploaded_data
            if uploaded_data["name"] not in [s["name"] for s in st.session_state.senaryolar]:
                st.session_state.senaryolar.append(uploaded_data)
            st.success(f"{uploaded_data['name']} yüklendi.")
        except Exception as e:
            st.error("Yükleme başarısız: " + str(e))

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

selected = option_menu(
    menu_title=None,
    options=["📊 Sonuçlar", "🗺️ Harita", "📅 Zaman Çizelgesi", "📈 Karşılaştırma", "🌍 Emisyon & Enerji"],
    icons=["bar-chart", "map", "calendar", "activity", "globe"],
    orientation="horizontal"
)

if selected == "📊 Sonuçlar":
    st.title("📊 Optimizasyon Sonuçları")
    if st.session_state.sonuc:
        s = st.session_state.sonuc
        st.write(f"**Senaryo:** {s['name']}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Toplam Mesafe (km)", f"{s['dist']:.2f}")
        col2.metric("Toplam Süre (dk)", f"{s['time']:.2f}")
        col3.metric("Toplam Risk", f"{s['risk']:.4f}")
        col4.metric("Ortalama Hız (km/s)", f"{s['avg_speed']:.2f}")
    else:
        st.info("Lütfen bir senaryo hesaplayın veya yükleyin.")

if selected == "🗺️ Harita":
    st.title("🗺️ Gerçek Yol Haritası")
    if st.session_state.sonuc:
        fmap = plot_folium_route(st.session_state.sonuc["route"], st.session_state.sonuc["log"])
        fmap.save("map.html")
        with open("map.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=600)
    else:
        st.warning("Harita için önce bir senaryo oluşturun veya yükleyin.")

if selected == "📅 Zaman Çizelgesi":
    st.title("📅 Gantt Grafiği")
    if st.session_state.sonuc:
        fig = plot_gantt(st.session_state.sonuc["log"])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Lütfen önce bir senaryo oluşturun veya yükleyin.")

if selected == "📈 Karşılaştırma":
    st.title("📈 Senaryo Karşılaştırması")
    if len(st.session_state.senaryolar) > 1:
        fig = plot_scenario_comparison(st.session_state.senaryolar)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Karşılaştırma için en az 2 senaryo kaydedilmelidir.")

if selected == "🌍 Emisyon & Enerji":
    st.title("🌍 Karbon Salınımı ve Enerji")
    if len(st.session_state.senaryolar) > 0:
        fig = plot_emission_energy_comparison(st.session_state.senaryolar)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Görselleştirme için en az 1 senaryo gereklidir.")
