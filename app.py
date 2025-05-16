
import streamlit as st
from streamlit_option_menu import option_menu
from optimizer import run_ga
from visualizer import plot_folium_route, plot_gantt, plot_scenario_comparison, plot_emission_energy_comparison
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Rota Optimizasyon Arayüzü")

if "results" not in st.session_state:
    st.session_state["results"] = []

with st.sidebar:
    secim = option_menu(
        menu_title="Menü",
        options=["Senaryo Oluştur", "Harita ve Rota", "Zaman Çizelgesi", "Karşılaştırmalar", "Duyarlılık Analizi", "Karbon Salınımı"],
        icons=["sliders", "map", "clock", "bar-chart", "activity", "leaf"],
        default_index=0,
    )

if secim == "Senaryo Oluştur":
    st.title("🧪 Senaryo Oluştur")
    st.markdown("Optimizasyon parametrelerini girin:")

    pop_size = st.slider("Popülasyon Büyüklüğü", 0, 5000, 300, 50)
    generations = st.slider("Nesil Sayısı", 0, 2500, 1000, 50)
    max_risk = st.slider("Maksimum Toplam Risk", 0.0, 10.0, 2.5, 0.1)
    hedef = st.selectbox("Amaç Fonksiyonu", ["Minimum Süre"])

    if st.button("✅ Genetik Algoritmayı Çalıştır"):
        with st.spinner("Optimizasyon çalışıyor..."):
            try:
                route, dist, time, risk, log = run_ga(pop_size, generations, max_risk, hedef)
                avg_speed = round(dist / (time / 60), 2) if time > 0 else 0
                name = f"{hedef} | Risk ≤ {max_risk}"

                st.session_state["results"].append({
                    "name": name,
                    "route": route,
                    "dist": dist,
                    "time": time,
                    "risk": risk,
                    "log": log,
                    "avg_speed": avg_speed
                })

                st.success("En iyi rota başarıyla bulundu!")
                st.write("🔁 Rota:", route)
                st.write(f"📏 Mesafe: {dist:.2f} km | ⏱ Süre: {time:.2f} dk | ☢ Risk: {risk:.2f} | 🚀 Ortalama Hız: {avg_speed:.2f} km/h")

            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")

elif secim == "Harita ve Rota":
    st.title("🗺️ Rota Haritası")
    if st.session_state["results"]:
        son = st.session_state["results"][-1]
        m = plot_folium_route(son["route"], son["log"])
        components.html(m._repr_html_(), height=600)
    else:
        st.warning("Lütfen önce bir senaryo çalıştırın.")

elif secim == "Zaman Çizelgesi":
    st.title("📊 Gantt Grafiği")
    if st.session_state["results"]:
        son = st.session_state["results"][-1]
        fig = plot_gantt(son["log"])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Önce bir senaryo çalıştırılmalı.")

elif secim == "Karşılaştırmalar":
    st.title("📈 Senaryo Karşılaştırması")
    if len(st.session_state["results"]) >= 2:
        fig1 = plot_scenario_comparison(st.session_state["results"])
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Kıyaslama için en az iki senaryo çalıştırmalısınız.")

elif secim == "Duyarlılık Analizi":
    st.title("🧬 Duyarlılık Analizi")
    st.write("Farklı hedeflerle çalıştırılan senaryolar karşılaştırılır.")
    if st.session_state["results"]:
        for r in st.session_state["results"]:
            st.markdown(f"**🎯 {r['name']}**")
            st.write(f"- 📏 Mesafe: {r['dist']} km")
            st.write(f"- ⏱ Süre: {r['time']} dk")
            st.write(f"- ☢ Risk: {r['risk']}")
            st.write(f"- 🚀 Ortalama Hız: {r['avg_speed']} km/h")
    else:
        st.warning("Henüz bir senaryo çalıştırmadınız.")

elif secim == "Karbon Salınımı":
    st.title("🌿 Karbon Salınımı ve Enerji Tüketimi")
    if st.session_state["results"]:
        fig2 = plot_emission_energy_comparison(st.session_state["results"])
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Gösterilecek veri bulunamadı.")
