def generate_recommendations(fusion, vision, audio):
    recs = []
    if not vision.get("samples") and not audio.get("segments"):
        recs.append("Upload a short consented sample video or WAV file to populate the optional signal-analysis panels.")
    if vision.get("samples"):
        counts = [x.get("visible_faces", 0) for x in vision["samples"]]
        if counts and max(counts) != min(counts):
            recs.append("Visible face counts vary across sampled frames. Review camera placement, lighting, and occlusion before interpreting the variation.")
        else:
            recs.append("Review sampled video frames manually; visible-face counts are not identity or attendance verification.")
    if audio.get("segments"):
        levels = [x.get("rms_level", 0) for x in audio["segments"]]
        if len(levels) > 1 and max(levels) > 2 * max(1, sum(levels) / len(levels)):
            recs.append("Audio activity varies over time. Consider checking whether the microphone position or background noise affects the recording.")
        else:
            recs.append("Use audio-level trends only as sound activity; do not infer who spoke or whether learners understood the topic.")
    if fusion["score"] < 40:
        recs.append("Consider a short recap, poll, or open question, and gather direct learner feedback rather than relying on sensor scores.")
    elif fusion["score"] >= 70:
        recs.append("If the session felt productive, note which teaching activities worked well and validate this with learner feedback.")
    else:
        recs.append("Consider a brief interactive activity and compare observations with instructor notes.")
    recs.append("Verify attendance manually, collect only necessary data, obtain consent, and define a retention/deletion policy.")
    return recs

def build_summary(session_name, session_date, expected_students, attendance_df, fusion, vision, audio):
    present = int(attendance_df["Present"].sum()) if not attendance_df.empty and "Present" in attendance_df else 0
    count = len(attendance_df)
    return {
        "session_name": session_name,
        "session_date": session_date,
        "expected_students": int(expected_students),
        "attendance_records": count,
        "present_in_records": present,
        "attendance_rate_percent": round(100 * present / count, 1) if count else None,
        "engagement_activity_index": fusion,
        "vision_summary": {k:v for k,v in vision.items() if k != "samples"},
        "audio_summary": {k:v for k,v in audio.items() if k != "segments"},
        "recommendations": generate_recommendations(fusion, vision, audio),
        "privacy_note": "Prototype only. Verify all records; sensor signals are not proof of attention, learning, or identity.",
    }
