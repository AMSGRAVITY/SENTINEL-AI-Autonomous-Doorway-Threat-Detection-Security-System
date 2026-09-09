import cv2
from threat_detection.tracking.tracker import Tracker
from threat_detection.face.recognizer import FaceRecognizer
from threat_detection.face.orientation import FaceOrientation
from threat_detection.face.mask_detector import MaskDetector

tracker = Tracker()

recognizer = FaceRecognizer(
    database_path=r"D:\AI_Projects\threat_detection\face\face_database.pkl"
)

mask_detector = MaskDetector()

def draw_person(frame, person):

    x1, y1, x2, y2 = map(int, person.bbox)

    color = get_box_color(person)

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        color,
        2
    )

    if person.has_face:
        x1, y1, x2, y2 = map(int, person.bbox)

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0,255,0),
            2
        )

    text = [
        f"ID : {person.track_id}",
        f"Name : {person.identity}",
        f"Match : {person.face_match_score:.2f}",
        f"Face : {person.has_face}",
        f"Masked : {person.masked}",
        f"Dir : {person.face_direction}",
        f"Changes : {person.direction_changes}",
    ]

    for i, line in enumerate(text):

        cv2.putText(
            frame,
            line,
            (x1, y1 - 10 - i*18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1
        )

    if person.face_landmarks is not None:
        for x, y in person.face_landmarks:
            cv2.circle(
                frame,
                (int(x), int(y)),
                2,
                (0,0,255),
                -1
            )

def get_box_color(person):

    # Highest priority
    if person.masked:
        return (0, 0, 255)      # Red

    if person.has_face:

        if person.identity != "Unknown":
            return (0, 255, 0)  # Green

        return (0, 255, 255)    # Yellow

    return (128, 128, 128)      # Gray

orientation = FaceOrientation()

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    people = tracker.update(frame)

    recognizer.update(frame, people)

    for person in people.values():
        orientation.update(person)
        mask_detector.update(frame, person)
        draw_person(frame, person)

    cv2.imshow("Face Debug", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break