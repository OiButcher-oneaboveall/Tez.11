
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

st.title("🚛 Rota Optimizasyonu")

col1, col2, col3 = st.columns(3)
with col1:
    pop_size = st.slider("Popülasyon Büyüklüğü", 10, 200, 100, step=10)
with col2:
    generations = st.slider("Nesil Sayısı", 10, 500, 200, step=10)
with col3:
    max_risk = st.slider("Maksimum Risk", 0.0, 1.0, 0.3, step=0.01)

isim = st.text_input("Senaryo İsmi", value=f"Senaryo-{len(st.session_state.senaryolar)+1}")
hesapla = st.button("🚀 Hesapla ve Kaydet")

# >>> SADECE ŞU KISIM EKLENDİ <<<
col_dl, col_up = st.columns(2)
with col_dl:
    if st.session_state.sonuc:
        st.download_button(
            "📤 JSON Kaydet",
            data=json.dumps(st.session_state.sonuc, indent=2),
            file_name=f"{st.session_state.sonuc['name']}.json",
            mime="application/json"
        )
with col_up:
    uploaded_file = st.file_uploader("📥 JSON Yükle", type=["json"])
    if uploaded_file:
        try:
            loaded = json.load(uploaded_file)
            st.session_state.sonuc = loaded
            if loaded["name"] not in [s["name"] for s in st.session_state.senaryolar]:
                st.session_state.senaryolar.append(loaded)
            st.success(f"{loaded['name']} yüklendi.")
        except Exception as e:
            st.error("Yükleme hatası: " + str(e))
# <<< SADECE BU KISIM EKLENDİ >>>

if hesapla:
    with st.spinner("Hesaplanıyor..."):
        route, dist, time, risk, log, avg_speed = run_ga(pop_size, generations, max_risk, "Minimum Süre")
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
    st.success("✅ Hesaplama tamamlandı!")

if st.session_state.sonuc:
    s = st.session_state.sonuc
    st.subheader("📊 Sonuçlar")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mesafe (km)", f"{s['dist']:.2f}")
    col2.metric("Süre (dk)", f"{s['time']:.2f}")
    col3.metric("Risk", f"{s['risk']:.4f}")
    col4.metric("Hız (km/s)", f"{s['avg_speed']:.2f}")

    st.subheader("🗺️ Harita")
    fmap = plot_folium_route(s["route"], s["log"])
    fmap.save("map.html")
    with open("map.html", "r", encoding="utf-8") as f:
        components.html(f.read(), height=600)

    st.subheader("📅 Gantt Grafiği")
    fig = plot_gantt(s["log"])
    st.plotly_chart(fig, use_container_width=True)
