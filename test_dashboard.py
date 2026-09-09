import cv2
import numpy as np

from threat_detection.ui.ui_manager import UIManager
from threat_detection.ui.event_logger import EventLogger

# Dummy Recorder
class DummyRecorder:
    def __init__(self, recording=False, recording_duration=18.0):
        self.recording = recording
        self.recording_duration = recording_duration

# Dummy Person Track
class DummyPerson:
    def __init__(
        self,
        track_id=1,
        bbox=(380, 180, 680, 620),
        identity="Unknown",
        confidence=0.82,
        movement="Standing",
        direction="Front",
        speed=15.2,
        threat_level="LOW",
        threat_score=20,
        should_record=False,
        should_alert=False,
        score_breakdown=None,
        threat_reasons=None,
        has_face=True,
        masked=False,
        loiter_time=35.0,
        loiter_score=20,
        weapon_detected=False
    ):
        self.track_id = track_id
        self.bbox = bbox
        self.identity = identity
        self.mask_confidence = confidence
        self.movement_state = movement
        self.face_direction = direction
        self.speed = speed
        self.threat_level = threat_level
        self.threat_score = threat_score
        self.should_record = should_record
        self.should_alert = should_alert
        self.score_breakdown = score_breakdown or {"Loitering": loiter_score}
        self.threat_reasons = threat_reasons or []
        self.has_face = has_face
        self.masked = masked
        self.loiter_time = loiter_time
        self.loiter_score = loiter_score
        self.weapon_detected = weapon_detected
        self.center_history = [((bbox[0]+bbox[2])//2, (bbox[1]+bbox[3])//2) for _ in range(5)]

# Test Scenarios
def create_test_people(mode):
    if mode == 1:
        # Monitoring Mode
        return {
            1: DummyPerson(
                threat_level="LOW",
                threat_score=18,
                score_breakdown={"Loitering": 5, "Face_Mask": 5, "Time": 5, "Movement": 3},
                masked=False,
                loiter_time=8.0,
                loiter_score=5
            )
        }, DummyRecorder(False)

    elif mode == 2:
        # HIGH Threat
        return {
            1: DummyPerson(
                track_id=1,
                threat_level="HIGH",
                threat_score=74,
                should_record=True,
                movement="Standing",
                direction="Left",
                masked=True,
                loiter_time=45.0,
                loiter_score=25,
                score_breakdown={
                    "Movement": 14,
                    "Face_Mask": 20,
                    "Loitering": 25,
                    "Night_Time": 15
                },
                threat_reasons=[
                    "Unknown Face Detected",
                    "Loitering > 30s",
                    "Frequent Head Turning"
                ]
            )
        }, DummyRecorder(True, recording_duration=24.0)

    elif mode == 3:
        # CRITICAL Threat with Weapon Detected
        return {
            1: DummyPerson(
                track_id=2,
                threat_level="CRITICAL",
                threat_score=96,
                movement="Running",
                direction="Right",
                speed=82.5,
                should_record=True,
                should_alert=True,
                masked=True,
                loiter_time=60.0,
                loiter_score=40,
                weapon_detected=True,
                score_breakdown={
                    "Rapid_Approach": 40,
                    "Face_Mask": 25,
                    "Weapon": 20,
                    "Night_Time": 11
                },
                threat_reasons=[
                    "Rapid Doorway Approach",
                    "Masked Identity",
                    "Weapon Detected"
                ]
            )
        }, DummyRecorder(True, recording_duration=42.0)

    elif mode == 4:
        # Multiple People
        return {
            1: DummyPerson(
                track_id=1,
                bbox=(150, 200, 380, 580),
                threat_level="LOW",
                threat_score=15,
                masked=False
            ),
            2: DummyPerson(
                track_id=2,
                bbox=(450, 180, 720, 600),
                threat_level="HIGH",
                threat_score=72,
                masked=True,
                loiter_time=50.0,
                score_breakdown={"Loitering": 30, "Face_Mask": 25, "Time": 17}
            ),
            3: DummyPerson(
                track_id=3,
                bbox=(800, 150, 1080, 650),
                threat_level="CRITICAL",
                threat_score=94,
                should_record=True,
                should_alert=True,
                masked=True,
                weapon_detected=True,
                score_breakdown={
                    "Rapid_Approach": 35,
                    "Face_Mask": 25,
                    "Restricted_Zone": 34
                },
                threat_reasons=[
                    "Weapon Detected",
                    "Aggressive Behaviour",
                    "Restricted Zone Violation"
                ]
            )
        }, DummyRecorder(True, recording_duration=31.0)


    elif mode == 5:
        # Known Person
        return {
            1: DummyPerson(
                identity="Maneesh",
                confidence=0.99,
                threat_level="SAFE",
                threat_score=10,
                should_record=False,
                score_breakdown={
                    "Movement": 5,
                    "Time": 5
                },
                threat_reasons=[]
            )
        }, DummyRecorder(False)

    elif mode == 6:
        # Empty Scene
        return {}, DummyRecorder(False)

    return {}, DummyRecorder(False)

# Main Dashboard Harness
ui_manager = UIManager(1920, 1080)
event_logger = EventLogger()
mode = 1

print("=" * 60)
print("SENTINEL-AI Command Center Dashboard Test")
print("=" * 60)
print("Keys 1-6 -> Switch Test Scenario")
print("1 -> Normal Monitoring Mode")
print("2 -> HIGH Threat Alert (REC ON)")
print("3 -> CRITICAL Threat Alert (REC ON + ALERT)")
print("4 -> Multiple Targets Detected")
print("5 -> Known Identified Person (Maneesh)")
print("6 -> Empty Doorway Scene")
print("ESC -> Exit Test Harness")
print("=" * 60)

while True:
    # Camera frame simulation background
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    for y in range(0, 720, 40):
        cv2.line(frame, (0, y), (1280, y), (35, 28, 22), 1)
    for x in range(0, 1280, 40):
        cv2.line(frame, (x, 0), (x, 720), (35, 28, 22), 1)

    # Get mock data
    people, recorder = create_test_people(mode)
    event_logger.update(people)

    # Render Command Center Dashboard canvas
    canvas = ui_manager.render(
        frame=frame,
        people=people,
        recorder=recorder,
        fps=29.8,
        event_logger=event_logger
    )

    # Display test mode badge
    cv2.putText(
        canvas,
        f"TEST MODE [{mode}]",
        (1770, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0, 240, 255),
        1,
        cv2.LINE_AA
    )

    cv2.imshow("SENTINEL-AI Command Center", canvas)

    key = cv2.waitKey(30) & 0xFF
    if key == 27:  # ESC
        break
    elif key in (ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6')):
        mode = int(chr(key))

cv2.destroyAllWindows()