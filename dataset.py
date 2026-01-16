import cv2
import face_recognition
import os


def create_dataset(name, reg_no):
    """
    Dataset collection using webcam
    """

    dataset_path = "attendance/dataset"
    person_path = os.path.join(dataset_path, f"{reg_no}_{name}")
    os.makedirs(person_path, exist_ok=True)

    cap = cv2.VideoCapture(0)
    count = 0

    print("[INFO] Dataset collection started")
    print("Press 's' to save image, 'q' to quit")

    while True:
        ret, frame = cap.read()

        if not ret or frame is None:
            print("Camera not working")
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(
            rgb_frame, model="hog"
        )

        for top, right, bottom, left in face_locations:
            cv2.rectangle(
                frame, (left, top), (right, bottom), (0, 255, 0), 2
            )

        cv2.imshow("Dataset Collection", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            if len(face_locations) == 1:
                count += 1
                cv2.imwrite(
                    os.path.join(person_path, f"{count}.jpg"),
                    frame
                )
                print(f"[SAVED] Image {count}")
            else:
                print("[WARNING] Show only ONE face")

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[SUCCESS] Dataset collection completed")
