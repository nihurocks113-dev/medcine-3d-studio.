

import os
import tempfile
from pathlib import Path

import streamlit as st

from pipeline import extract_content
from render_3d import render_lumbar_spine


st.set_page_config(
    page_title="MedCine 3D Studio",
    page_icon="🧬",
    layout="wide",
)

st.title("🧬 MedCine 3D Studio")
st.write(
    "Upload medical PDFs or notes images and create "
    "an educational 3D animation prototype."
)

st.info(
    "Current prototype: uploads are extracted for review, "
    "and a predefined simplified 3D lumbar spine animation "
    "is rendered. The uploaded content does not yet change "
    "the 3D anatomy automatically."
)

uploaded_files = st.file_uploader(
    "Upload PDFs or medical notes images",
    type=[
        "pdf", "png", "jpg", "jpeg", "webp",
        "txt", "md", "docx", "pptx",
    ],
    accept_multiple_files=True,
)

topic = st.text_input(
    "Medical topic",
    value="Lumbar spine anatomy",
)

duration = st.slider(
    "3D demo duration (seconds)",
    min_value=8,
    max_value=30,
    value=12,
)

if st.button("Extract notes and generate 3D video"):
    if not uploaded_files:
        st.warning("Please upload at least one PDF or image.")
        st.stop()

    with tempfile.TemporaryDirectory() as folder:
        extracted_sections = []

        progress = st.progress(0)
        status = st.empty()

        for index, uploaded in enumerate(uploaded_files):
            status.write(
                f"Reading {uploaded.name}..."
            )

            safe_name = Path(uploaded.name).name
            file_path = os.path.join(folder, safe_name)

            with open(file_path, "wb") as file:
                file.write(uploaded.getvalue())

            try:
                content = extract_content(file_path)
                if content.strip():
                    extracted_sections.append(
                        f"FILE: {safe_name}\n\n{content}"
                    )
                else:
                    extracted_sections.append(
                        f"FILE: {safe_name}\n"
                        "No readable text was extracted."
                    )
            except Exception as error:
                extracted_sections.append(
                    f"FILE: {safe_name}\n"
                    f"Extraction error: {error}"
                )

            progress.progress(
                (index + 1) / len(uploaded_files)
            )

        combined_text = "\n\n".join(extracted_sections)

        st.session_state["extracted_text"] = combined_text
        st.session_state["topic"] = topic

        status.write("Rendering the 3D demo...")

        output_path = os.path.join(
            folder,
            "medcine_lumbar_spine.mp4",
        )

        try:
            render_lumbar_spine(
                output_path=output_path,
                duration_seconds=duration,
                fps=12,
                resolution=640,
            )

            with open(output_path, "rb") as video_file:
                video_bytes = video_file.read()

            st.session_state["video_bytes"] = video_bytes
            status.success("3D demo rendered successfully!")

        except Exception as error:
            status.error(
                f"Rendering failed: {error}"
            )

if "extracted_text" in st.session_state:
    st.subheader("Extracted notes")
    st.caption(
        "Review this text to check whether the PDF or image "
        "was read correctly."
    )

    st.text_area(
        "Extracted content",
        value=st.session_state["extracted_text"],
        height=220,
    )

if "video_bytes" in st.session_state:
    st.subheader("Generated 3D educational demo")

    st.video(st.session_state["video_bytes"])

    st.download_button(
        "Download 3D video (MP4)",
        data=st.session_state["video_bytes"],
        file_name="medcine_lumbar_spine.mp4",
        mime="video/mp4",
    )

    st.caption(
        "Educational prototype only. The animation is a "
        "simplified model, not a clinically accurate rendering."
    )
