import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import tempfile
from src.analytics import build_summary, generate_recommendations
from src.fusion import calculate_engagement
from src.vision import analyze_video
from src.audio import analyze_wav

st.set_page_config(page_title="Multimodal Attendance & Engagement Agent", page_icon="🎓", layout="wide")
st.title("🎓 Multimodal Attendance & Engagement Agent")
st.caption("Offline-first classroom prototype | Vision + audio activity + analytics + teaching suggestions")

st.warning(
    "Prototype and decision-support tool only. Face counts do not identify people, and audio/visual signals "
    "cannot reliably prove attention or learning. Use consented media, verify attendance manually, and do not "
    "use scores for grading or disciplinary decisions."
)

with st.sidebar:
    st.header("Session setup")
    session_name = st.text_input("Session name", "Demo Classroom Session")
    session_date = st.date_input("Session date", datetime.now().date())
    expected_students = st.number_input("Expected students", min_value=1, max_value=500, value=30)
    presence_seconds = st.slider("Sustained presence threshold (seconds)", 1, 60, 10)
    st.divider()
    st.write("Demo mode")
    use_demo = st.toggle("Show sample attendance and engagement data", value=True)

tab_overview, tab_attendance, tab_vision, tab_audio, tab_insights = st.tabs(
    ["Overview", "Attendance", "Vision module", "Audio module", "Analytics & suggestions"]
)

def demo_attendance():
    return pd.DataFrame({
        "Participant ID": [f"STU-{i:03d}" for i in range(1, 11)],
        "Present": [True, True, True, False, True, True, False, True, True, False],
        "First detected": ["09:00:05", "09:00:11", "09:00:17", "—", "09:00:22", "09:00:08", "—", "09:00:31", "09:00:44", "—"],
        "Duration (minutes)": [48, 46, 42, 0, 44, 47, 0, 39, 35, 0],
    })

if "vision_result" not in st.session_state:
    st.session_state.vision_result = None
if "audio_result" not in st.session_state:
    st.session_state.audio_result = None

with tab_overview:
    st.subheader("Session overview")
    att = demo_attendance() if use_demo else pd.DataFrame(columns=["Participant ID", "Present", "First detected", "Duration (minutes)"])
    if not use_demo:
        st.info("Upload a CSV in the Attendance tab to display your own records.")
    present = int(att["Present"].sum()) if not att.empty else 0
    rate = round(present / len(att) * 100, 1) if len(att) else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Session", session_name)
    c2.metric("Present (records)", present)
    c3.metric("Attendance rate", f"{rate}%")
    c4.metric("Expected class size", int(expected_students))
    if not att.empty:
        left, right = st.columns(2)
        with left:
            st.write("#### Attendance distribution")
            st.bar_chart(pd.DataFrame({"Students": [present, len(att)-present]}, index=["Present", "Absent"]))
        with right:
            st.write("#### Sample attendance log")
            st.dataframe(att, use_container_width=True, hide_index=True)
        st.download_button("Download attendance CSV", att.to_csv(index=False), "attendance_log.csv", "text/csv")
    if st.session_state.vision_result:
        st.write("#### Latest vision result")
        st.json(st.session_state.vision_result)
    if st.session_state.audio_result:
        st.write("#### Latest audio result")
        st.json(st.session_state.audio_result)

with tab_attendance:
    st.subheader("Attendance log")
    st.write("Use anonymized participant IDs. This prototype intentionally does not perform face recognition or infer identity.")
    uploaded = st.file_uploader("Upload attendance CSV", type=["csv"], key="attendance_csv")
    if uploaded:
        try:
            records = pd.read_csv(uploaded)
            st.dataframe(records, use_container_width=True, hide_index=True)
            st.download_button("Download reviewed CSV", records.to_csv(index=False), "reviewed_attendance.csv", "text/csv")
        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")
    elif use_demo:
        st.dataframe(demo_attendance(), use_container_width=True, hide_index=True)
    st.caption(f"Session: {session_name} | Date: {session_date} | Threshold setting: {presence_seconds} seconds")

with tab_vision:
    st.subheader("EPIC 2 — Vision module")
    st.write("Upload a short consented video. The module samples frames and estimates visible face counts; it does not identify individuals.")
    video = st.file_uploader("Video file (MP4, AVI, MOV)", type=["mp4", "avi", "mov"], key="video")
    if video and st.button("Analyze video", key="analyze_video"):
        with st.spinner("Sampling video frames…"):
            try:
                suffix = Path(video.name).suffix or ".mp4"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(video.getvalue())
                    tmp_path = tmp.name
                result = analyze_video(tmp_path)
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                st.session_state.vision_result = result
                st.success("Video sampling completed.")
                st.json(result)
                if result.get("samples"):
                    chart = pd.DataFrame(result["samples"])
                    st.line_chart(chart.set_index("sample")["visible_faces"])
            except Exception as exc:
                st.error(f"Vision analysis failed: {exc}")
                st.info("Check that OpenCV is installed and the uploaded video is readable.")
    elif not video:
        st.caption("No video is required to explore the dashboard.")

with tab_audio:
    st.subheader("EPIC 3 — Audio module")
    st.write("Upload a consented WAV file to estimate sound activity by time segment. This measures sound energy only; it does not recognize speech content or speakers.")
    audio = st.file_uploader("Audio file (WAV)", type=["wav"], key="audio")
    if audio and st.button("Analyze audio", key="analyze_audio"):
        try:
            result = analyze_wav(audio.getvalue())
            st.session_state.audio_result = result
            st.success("Audio analysis completed.")
            st.metric("Duration", f"{result['duration_seconds']} seconds")
            if result.get("segments"):
                chart = pd.DataFrame(result["segments"])
                st.line_chart(chart.set_index("second")["rms_level"])
            st.json({k:v for k,v in result.items() if k != "segments"})
        except Exception as exc:
            st.error(f"Audio analysis failed: {exc}")
    elif not audio:
        st.caption("WAV audio is optional. The rest of the project works without it.")

with tab_insights:
    st.subheader("EPIC 4 & 5 — Signal fusion, engagement profile and recommendations")
    vision = st.session_state.vision_result or {"average_visible_faces": 0, "samples": []}
    audio = st.session_state.audio_result or {"average_rms": 0, "segments": [], "duration_seconds": 0}
    fusion = calculate_engagement(vision, audio)
    st.metric("Illustrative session activity score", f"{fusion['score']}/100")
    st.caption(f"Indicator level: {fusion['label']} — this is a rough signal summary, not a measure of a person's attention.")
    st.write("#### Teaching suggestions")
    for item in generate_recommendations(fusion, vision, audio):
        st.markdown(f"- {item}")
    summary = build_summary(session_name, str(session_date), expected_students, demo_attendance() if use_demo else pd.DataFrame(), fusion, vision, audio)
    st.write("#### Session summary")
    st.json(summary)
    st.download_button("Download session summary JSON", pd.Series(summary).to_json(indent=2), "session_summary.json", "application/json")

st.divider()
st.caption("Local prototype. Uploaded media is processed during the current app session; do not upload sensitive classroom recordings.")
