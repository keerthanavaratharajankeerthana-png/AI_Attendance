import os
import pickle
import face_recognition
import streamlit as st


def encode_faces():
    DATASET_DIR = "attendance/dataset"
    ENCODINGS_DIR = "encodings"
    ENCODINGS_FILE = os.path.join(ENCODINGS_DIR, "face_encodings.pkl")

    os.makedirs(ENCODINGS_DIR, exist_ok=True)

    known_encodings = []
    known_names = []

    status = st.empty()
    progress_bar = st.progress(0)

    if not os.path.exists(DATASET_DIR):
        status.error("❌ Dataset folder not found")
        return False

    persons = [
        p for p in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, p))
    ]

    if len(persons) == 0:
        status.warning("⚠️ No student datasets available")
        return False

    total_images = sum(
        len(os.listdir(os.path.join(DATASET_DIR, p)))
        for p in persons
    )

    if total_images == 0:
        status.warning("⚠️ No images found in dataset")
        return False

    processed = 0
    status.info("🧠 Encoding faces... Please wait")

    with st.spinner("Encoding in progress..."):
        for person in persons:
            person_path = os.path.join(DATASET_DIR, person)
            status.info(f"📂 Processing: {person}")

            for img_name in os.listdir(person_path):
                img_path = os.path.join(person_path, img_name)

                try:
                    image = face_recognition.load_image_file(img_path)
                    face_locations = face_recognition.face_locations(image, model="hog")
                    face_encs = face_recognition.face_encodings(image, face_locations)

                    if len(face_encs) == 0:
                        status.warning(f"⚠️ No face detected: {img_name}")
                        continue

                    for enc in face_encs:
                        known_encodings.append(enc)
                        known_names.append(person)

                    processed += 1
                    progress = int((processed / total_images) * 100)
                    progress_bar.progress(min(progress, 100))

                except Exception as e:
                    status.error(f"❌ Error processing {img_name}")

    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(
            {"encodings": known_encodings, "names": known_names},
            f
        )

    status.success(f"✅ Encoding completed | Total faces encoded: {len(known_encodings)}")
    return True