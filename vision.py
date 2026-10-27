def analyze_video(video_path, max_samples=20):
    """Estimate visible faces in sampled video frames; never identifies people."""
    import cv2
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Video could not be opened.")
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
    step = max(1, total // max_samples) if total else 10
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    samples, frame_index = [], 0
    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        if frame_index % step == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            samples.append({
                "sample": len(samples) + 1,
                "timestamp_seconds": round(frame_index / fps, 2) if fps > 0 else None,
                "visible_faces": int(len(faces)),
            })
            if len(samples) >= max_samples:
                break
        frame_index += 1
    cap.release()
    counts = [x["visible_faces"] for x in samples]
    return {
        "method": "OpenCV Haar cascade sampled-frame face count",
        "frames_total": total,
        "samples_count": len(samples),
        "average_visible_faces": round(sum(counts) / len(counts), 2) if counts else 0,
        "maximum_visible_faces": max(counts) if counts else 0,
        "samples": samples,
        "limitation": "Face counts do not identify students and are not proof of attendance or engagement.",
    }
