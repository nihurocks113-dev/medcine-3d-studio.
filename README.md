
# MedCine 3D Studio

Convert medical documents into educational storyboard videos.

## Features

- Upload PDF, DOCX, TXT and image files
- Extract readable medical text
- Create a basic educational storyboard locally
- Render scenes into an MP4 video
- No OpenAI API key required for this basic workflow

## Installation

Install Python 3.10 or newer.

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Run the application

```bash
streamlit run app.py
```

## Important limitations

- Scanned PDFs may require OCR.
- Image OCR requires the Tesseract executable.
- The current renderer produces educational scene cards.
- It does not generate realistic 3D anatomy, animated organs,
  or AI-generated medical illustrations.
- No narration audio is generated in this basic version.

## Medical accuracy

Review all generated educational content against trusted
medical references before using it for teaching.

