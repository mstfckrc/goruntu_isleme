import streamlit as st
import os
from controller.video.youtube_downloader import download_with_ytdlp
from controller.video.analyze_recorded_video import analyze_recorded_video
from controller.video.fix_video import reencode_video
import pandas as pd

st.set_page_config(page_title="Konuşan Kişi Tanıma", layout="centered")
st.title("🧠 Konuşan Kişi Tanıma Sistemi")

sekme = st.tabs(["📡 Canlı Video", "🎞️ Kayıtlı Video (YouTube)"])

# --- Sekme 1: Canlı Video (User Story 1) ---
with sekme[0]:
    st.header("📡 Canlı Video Üzerinden Konuşan Tanıma")
    st.markdown("Bu modül canlı kamera akışında konuşan kişiyi tanımlar.\n\n🟢 Uygulama dışı başlatılacak.")
    st.info("👉 Bu özellik uygulama dışında `live_speaker_tracker.py` ile test edilmelidir.")
    st.code("python controller/face/live_speaker_tracker.py")

# --- Sekme 2: Kayıtlı Video Analizi (User Story 2) ---
with sekme[1]:
    st.header("🎞️ YouTube Videosu Üzerinden Konuşan Tanıma")
    url = st.text_input("🔗 YouTube video linkini girin")
    filename = st.text_input("💾 Video dosya adı (örnek: konusma.mp4)", "konusma.mp4")

    if st.button("🔍 Videoyu İndir ve Analiz Et"):
        if not filename.endswith(".mp4"):
            filename += ".mp4"

        with st.spinner("📥 Video indiriliyor..."):
            raw_path = download_with_ytdlp(url, filename=filename)
            fixed_path = reencode_video(raw_path)

        st.success("🎬 Video başarıyla indirildi ve dönüştürüldü.")

        st.video(fixed_path)

        with st.spinner("🧠 Video analiz ediliyor..."):
            results = analyze_recorded_video(fixed_path)

        if results:
            st.success("✅ Analiz tamamlandı!")
            df = pd.DataFrame(list(results.items()), columns=["Kişi", "Konuşma Süresi (sn)"])
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Sonuçları CSV olarak indir", data=csv, file_name="konusma_sureleri.csv")
        else:
            st.warning("❗ Videoda tanımlanabilen kişi bulunamadı.")
