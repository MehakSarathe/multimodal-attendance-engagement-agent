def calculate_engagement(vision_result, audio_result):
    """
    Transparent illustrative activity index from available video/audio signals.
    This is not a validated psychological attention score.
    """
    face_avg = float(vision_result.get("average_visible_faces", 0) or 0)
    audio_avg = float(audio_result.get("average_rms", 0) or 0)
    # Normalize rough activity indicators into bounded sub-scores.
    visual_score = min(100.0, face_avg * 20.0)
    # RMS scaling depends on recording format; cap to avoid dominating the score.
    audio_score = min(100.0, audio_avg / 100.0)
    if vision_result.get("samples") and audio_result.get("segments"):
        score = 0.65 * visual_score + 0.35 * audio_score
        available = "video and audio"
    elif vision_result.get("samples"):
        score, available = visual_score, "video only"
    elif audio_result.get("segments"):
        score, available = audio_score, "audio only"
    else:
        score, available = 50.0, "no media uploaded; neutral demo placeholder"
    score = round(max(0.0, min(100.0, score)), 1)
    label = "higher observed activity" if score >= 70 else "moderate observed activity" if score >= 40 else "lower observed activity"
    return {
        "score": score,
        "label": label,
        "signals_available": available,
        "visual_subscore": round(visual_score, 1),
        "audio_subscore": round(audio_score, 1),
        "interpretation": "Illustrative activity index only; not a validated attention or learning measure.",
    }
