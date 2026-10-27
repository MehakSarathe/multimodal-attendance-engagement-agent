# Multimodal Attendance & Engagement Agent

A student-project prototype aligned with the Skillwallet project description. It includes attendance-log review, sampled video face-count estimation, audio signal energy analysis, a transparent illustrative signal-fusion index, session summaries, and rule-based teaching suggestions.

## Modules
- **EPIC 1 — Environment:** dependency list and setup instructions.
- **EPIC 2 — Vision:** OpenCV sampled-frame face-count estimation.
- **EPIC 3 — Audio:** WAV sound-energy (RMS) analysis.
- **EPIC 4 — AI / fusion:** transparent combination of available activity indicators.
- **EPIC 5 — Analytics:** summary JSON and teaching suggestions.
- **EPIC 6 — Interface/testing:** Streamlit dashboard with CSV/JSON downloads.

## Requirements
Python 3.10 or 3.11 recommended, Git, Chrome/Edge. A webcam is not required; video/audio uploads are optional.

## Run on Windows
```powershell
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```
Open the local URL shown by Streamlit, usually `http://localhost:8501`.

## Run on macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## GitHub
Upload `app.py`, `requirements.txt`, `README.md`, and the complete `src/` folder. Do not upload `.venv/`, private student data, recordings, or API keys.

## Demo deployment
A Streamlit-compatible host can deploy this repository. Set the main file path to `app.py` and install dependencies from `requirements.txt`. A GitHub URL is the source-code link; the hosted application URL is the demo link.

## Limitations and ethical use
This is a prototype, not a production biometric attendance product. Face counts do not identify individuals; sound energy does not identify speakers; neither is proof of attention, learning, or participation. The activity index is illustrative and not scientifically validated. Use consented sample data, manually verify records, avoid high-impact decisions based on sensor scores, and define retention/deletion policies.
