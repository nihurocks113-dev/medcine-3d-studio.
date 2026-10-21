
import os
import re
import textwrap
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


def extract_content(uploaded_file):
    """Extract readable text from an uploaded medical file."""
    name = uploaded_file.name.lower()
    content = ""

    try:
        uploaded_file.seek(0)

        if name.endswith(".txt"):
            content = uploaded_file.read().decode(
                "utf-8", errors="ignore"
            )

        elif name.endswith(".pdf"):
            if PdfReader is None:
                raise RuntimeError("Install pypdf first.")

            reader = PdfReader(uploaded_file)
            content = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

        elif name.endswith(".docx"):
            if Document is None:
                raise RuntimeError("Install python-docx first.")

            document = Document(uploaded_file)
            content = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

        elif name.endswith((".png", ".jpg", ".jpeg")):
            try:
                import pytesseract

                image = Image.open(uploaded_file).convert("RGB")
                content = pytesseract.image_to_string(image)

            except Exception:
                content = (
                    "Image uploaded successfully. "
                    "OCR is unavailable. Please enter the "
                    "medical text manually."
                )

        else:
            raise ValueError("Unsupported file format.")

    except Exception as exc:
        raise RuntimeError(
            f"Could not read the uploaded file: {exc}"
        ) from exc

    if not content.strip():
        raise ValueError(
            "No readable text found. Scanned PDFs may need OCR."
        )

    return content.strip()


def generate_storyboard(content, max_scenes=8):
    """Create a basic educational storyboard locally."""
    if not content or not content.strip():
        raise ValueError("Medical content is empty.")

    clean_text = re.sub(r"\s+", " ", content).strip()

    # Split text into readable chunks.
    sentences = re.split(r"(?<=[.!?])\s+", clean_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        sentences = [clean_text]

    chunk_size = max(1, (len(sentences) + max_scenes - 1)
                     // max_scenes)

    scenes = []

    for index in range(0, len(sentences), chunk_size):
        if len(scenes) >= max_scenes:
            break

        chunk = " ".join(sentences[index:index + chunk_size])

        scenes.append({
            "title": f"Medical Concept {len(scenes) + 1}",
            "narration": chunk,
            "visual": (
                "Educational medical illustration: "
                + chunk[:250]
            ),
            "duration": 6
        })

    return scenes


def _get_font(size):
    """Use a system font if available."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]

    for font_path in candidates:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except OSError:
                pass

    return ImageFont.load_default()


def _make_scene_image(scene, output_path, width=1280, height=720):
    """Render a clean educational scene card."""
    image = Image.new("RGB", (width, height), "#101827")
    draw = ImageDraw.Draw(image)

    title_font = _get_font(42)
    body_font = _get_font(27)
    small_font = _get_font(20)

    draw.rectangle(
        (0, 0, width, 14),
        fill="#38BDF8"
    )

    draw.text(
        (65, 55),
        "MEDCINE 3D STUDIO",
        font=small_font,
        fill="#7DD3FC"
    )

    draw.text(
        (65, 115),
        scene.get("title", "Medical Concept"),
        font=title_font,
        fill="white"
    )

    visual = scene.get("visual", "")
    narration = scene.get("narration", "")

    draw.text(
        (65, 205),
        "VISUAL",
        font=small_font,
        fill="#38BDF8"
    )

    visual_lines = textwrap.wrap(visual, width=62)[:5]
    y = 245

    for line in visual_lines:
        draw.text((65, y), line, font=body_font, fill="#E5E7EB")
        y += 43

    draw.line(
        (65, 485, width - 65, 485),
        fill="#334155",
        width=2
    )

    draw.text(
        (65, 510),
        "EDUCATIONAL NOTES",
        font=small_font,
        fill="#7DD3FC"
    )

    notes_lines = textwrap.wrap(narration, width=78)[:4]
    y = 550

    for line in notes_lines:
        draw.text((65, y), line, font=small_font, fill="white")
        y += 31

    image.save(output_path, quality=95)


def render_video(storyboard, output_path=None):
    """Render storyboard scenes into an MP4 video."""
    if not storyboard:
        raise ValueError("No scenes available to render.")

    try:
        import imageio.v2 as imageio
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "Install imageio and numpy using requirements.txt."
        ) from exc

    if output_path is None:
        output_path = os.path.join(
            tempfile.gettempdir(), "medcine_video.mp4"
        )

    temp_dir = tempfile.mkdtemp(prefix="medcine_")
    fps = 24

    try:
        with imageio.get_writer(
            output_path,
            fps=fps,
            codec="libx264",
            macro_block_size=16
        ) as writer:

            for scene in storyboard:
                frame_path = os.path.join(
                    temp_dir, f"scene_{storyboard.index(scene)}.png"
                )

                _make_scene_image(scene, frame_path)

                frame = np.array(
                    Image.open(frame_path).convert("RGB")
                )

                duration = max(
                    2, min(int(scene.get("duration", 6)), 30)
                )

                for _ in range(fps * duration):
                    writer.append_data(frame)

        return output_path

    except Exception as exc:
        raise RuntimeError(
            "Video rendering failed. Check FFmpeg support and "
            f"dependencies. Details: {exc}"
        ) from exc
