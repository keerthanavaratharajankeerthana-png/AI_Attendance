import cv2
import pickle
import face_recognition

import numpy as np
import requests
import streamlit as st
from datetime import datetime, date, time

# ================= CONFIG =================
ENCODINGS_FILE = "encodings/face_encodings.pkl"

# n8n webhook
N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/attendance"

# ⏰ TIME RULES
PRESENT_END = time(9, 5, 0)   # 09:05
LATE_END = time(9, 10, 0)     # 09:10
# =========================================


def start_attendance():
    """
    Starts live attendance camera
    Shows live status in Streamlit UI
    Returns: list of (name, status)
    """

    status_box = st.status("🔄 Initializing attendance system...", expanded=True)
    attendance_container = st.container()
    results = []

    # ---------- Load encodings ----------
    try:
        status_box.update(label="📦 Loading face encodings...", state="running")

        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)

        known_encodings = data["encodings"]
        known_names = data["names"]

        if len(known_names) == 0:
            status_box.update(label="❌ No face encodings found", state="error")
            return []

        status_box.update(
            label=f"✅ Loaded {len(known_names)} known faces",
            state="complete"
        )

    except Exception as e:
        status_box.update(label="❌ Failed to load encodings", state="error")
        st.error(str(e))
        return []

    # ---------- Camera ----------
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("❌ Camera not accessible")
        return []

    st.info("🎥 Attendance camera running (Press **Q** to stop)")
    THRESHOLD = 0.45
    attendance_marked = set()

    with st.spinner("🔍 Face recognition in progress..."):
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, boxes)

            for (top, right, bottom, left), face_encoding in zip(boxes, encodings):

                matches = face_recognition.compare_faces(
                    known_encodings, face_encoding, tolerance=THRESHOLD
                )
                face_distances = face_recognition.face_distance(
                    known_encodings, face_encoding
                )

                name = "Unknown"
                status = ""

                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = known_names[best_match_index]

                        if name not in attendance_marked:
                            attendance_marked.add(name)

                            now = datetime.now()
                            today_date = str(date.today())
                            time_now = now.strftime("%H:%M:%S")
                            current_time = now.time()

                            # ---- PRESENT / LATE / ABSENT ----
                            if current_time <= PRESENT_END:
                                status = "Present"
                            elif current_time <= LATE_END:
                                status = "Late Coming"
                            else:
                                status = "Absent"

                            payload = {
                                "name": name,
                                "date": today_date,
                                "time": time_now,
                                "status": status
                            }

                            try:
                                requests.post(
                                    N8N_WEBHOOK_URL,
                                    json=payload,
                                    timeout=5
                                )
                            except:
                                pass

                            results.append((name, status))

                            # ---- LIVE UI UPDATE ----
                            with attendance_container:
                                if status == "Present":
                                    st.success(f"✅ {name} → Present")
                                elif status == "Late Coming":
                                    st.warning(f"🕒 {name} → Late Coming")
                                else:
                                    st.error(f"❌ {name} → Absent")

                # ---- Bounding Box Colors ----
                if status == "Present":
                    color = (0, 255, 0)
                elif status == "Late Coming":
                    color = (0, 255, 255)
                else:
                    color = (0, 0, 255)

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(
                    frame,
                    f"{name} {status}",
                    (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2,
                )

            cv2.imshow("Attendance Camera (Press Q to stop)", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

    st.success("🎉 Attendance session completed")
    return results