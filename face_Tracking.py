import cv2
from pathlib import Path

xml_path = Path(__file__).parent / "haarcascade_frontalface_default.xml"

face_cascade = cv2.CascadeClassifier(str(xml_path))

if face_cascade.empty():
    print("Error: XML file could not be loaded")
    print("Looking here:", xml_path)
    exit()

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture image")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        1.1,
        5,
        0,
        (30, 30)
    )

    for x, y, w, h in faces:
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (255, 0, 0),
            2
        )

    # Count the number of detected faces
    people_count = len(faces)

    # Display the people count
    cv2.putText(
        frame,
        f"People Count: {people_count}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 0, 0),
        2,
        cv2.LINE_AA
    )

    cv2.imshow("Face Detection - Press q to Exit", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()