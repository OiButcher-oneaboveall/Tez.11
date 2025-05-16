
import streamlit as st
import json
from optimizer import run_ga
from visualizer import plot_gantt, plot_folium_route
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Rota Optimizasyonu")

if "sonuc" not in st.session_state:
    st.session_state.sonuc = None
if "senaryolar" not in st.session_state:
    st.session_state.senaryolar = []

st.title("🚛 Rota Optimizasyon Uygulaması")

with st.sidebar:
    st.header("Parametreler")
    pop_size = st.slider("Popülasyon Büyüklüğü", 10, 200, 50, step=10)
    generations = st.slider("Nesil Sayısı", 10, 500, 100, step=10)
    max_risk = st.slider("Maksimum Risk", 0.0, 15.0, 0.3, step=0.1)
    hedef = st.selectbox("Amaç Fonksiyonu", [
        "Minimum Süre", "Minimum Mesafe", "Minimum Risk", "Maksimum Ortalama Hız"
    ])
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
            data = json.load(uploaded_file)
            st.session_state.sonuc = data
            if data["name"] not in [s["name"] for s in st.session_state.senaryolar]:
                st.session_state.senaryolar.append(data)
            st.success(f"{data['name']} yüklendi.")
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
