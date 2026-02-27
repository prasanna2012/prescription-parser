# MediExplain

**MediExplain** is a Streamlit app that interprets handwritten-style digital prescriptions, explains dosage instructions in local languages (Telugu/Hindi), and provides audio output.

## Features
- Upload prescription images
- Extract text using OCR
- Simplify and translate text to local language
- Generate voice output (TTS)
- Optional history of previous prescriptions

## Folder Structure
- `app.py` : Main Streamlit app
- `utils.py` : Helper functions for OCR, translation, TTS
- `assets/` : Images/icons
- `output_audio/` : Store generated audio
- `history_data/` : Optional history storage
- `requirements.txt` : Python packages

## How to Run
1. Install dependencies: