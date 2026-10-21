
import streamlit as st
from pipeline import extract_content, generate_storyboard, render_video
import os
import tempfile

st.set_page_config(page_title="MedCine 3D Studio", layout="wide")
st.title("🧬 MedCine 3D Studio")
st.write("Turn medical documents into educational videos.")

uploaded = st.file_uploader(
    "Upload a medical image or document",
    type=["png", "jpg", "jpeg", "webp", "pdf", "txt", "docx", "pptx"]
)

topic = st.text_input("Medical topic")
duration = st.slider("Video duration (minutes)", 1, 10, 2)
language = st.selectbox("Narration language", ["English", "Hindi", "Hinglish"])

if st.button("Generate video"):
    if not uploaded:
        st.warning("Please upload a file first.")
    elif not os.getenv("OPENAI_API_KEY"):
        st.error("API key is not configured yet.")
    else:
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, uploaded.name)
            with open(path, "wb") as f:
                f.write(uploaded.getvalue())

            with st.spinner("Analysing medical material..."):
                content = extract_content(path)
                scenes = generate_storyboard(
                    content, topic, duration, language,
                    "Cinematic medical", True
                )
                output = os.path.join(folder, "medcine_video.mp4")
                render_video(
                    scenes, output, duration, "720p", True
                )

            with open(output, "rb") as f:
                video = f.read()

            st.video(video)
            st.download_button(
                "Download MP4",
                video,
                file_name="medcine_video.mp4",
                mime="video/mp4"
            )
