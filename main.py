import time, cv2
from threat_detection.pipeline.pipeline_detection import DetectionPipeline
from threat_detection.ui.ui_manager import UIManager
from threat_detection.media.recording.recorder import ThreadedRecorder
from threat_detection.media.snapshot.snapshot import SnapshotSaver
from threat_detection.alert.alert_manager import AlertManager
from threat_detection.ui.event_logger import EventLogger

import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="insightface")

TARGET_FPS = 30
FRAME_TIME = 1.0 / TARGET_FPS

def main():
    # 1. Camera Setup
    print("Started Main Loop")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        raise RuntimeError("Could not open camera")
    print("Webcam On")


    # 2. Subsystem Initialization
    ui = UIManager()
    print("[DEBUG] UI done")
    pipeline = DetectionPipeline()
    print("[DEBUG] pipeline Done")
    snapshot_saver = SnapshotSaver()
    print("[DEBUG] snapshot done")
    alert_manager = AlertManager()
    print("[DEBUG] alert done")
    event_logger = EventLogger()
    print("[DEBUG] event done")
    recorder = ThreadedRecorder()
    print("[DEBUG] recorder done")

    previous_time = time.time() 
    people = {}
    # ======================================================
    # Main Loop
    # ======================================================
    try:
        while True:

            success, frame = cap.read()
            if not success:
                break

            # FPS Calculation
            current_time = time.time()
            fps = 1 / max(current_time - previous_time, 1e-6)
            previous_time = current_time

            # --- Detection & Analysis ---
            people = pipeline.process(frame)
            event_logger.update(people)

            # --- Threat Level Evaluation ---
            highest_person = alert_manager.get_highest_person(people)
            threat_level = getattr(highest_person, "threat_level", "LOW") if highest_person else "LOW"

            # --- Recording & Two-Stage Alert Logic ---
            if threat_level in ["HIGH", "CRITICAL"]:
                # Start recording if not already active
                if not recorder.recording:
                    recorder.start()
                    alert_manager.start_session()

                # Stage 1: Send Immediate Alert when CRITICAL
                if threat_level == "CRITICAL" and not alert_manager.critical_triggered:
                    snapshot_path = snapshot_saver.capture(frame, prefix=f"threat_id_{highest_person.track_id}")
                    # Non-blocking async dispatch
                    alert_manager.send_immediate_alert_async(people, snapshot_path)

            else:
                # Stage 2: Stop Recording & Send Follow-up when threat drops below HIGH
                if recorder.recording:
                    video_path = recorder.stop()
                    # Non-blocking async dispatch
                    alert_manager.send_video_followup_async(video_path)

            # Update recorder buffer with current frame
            recorder.update(frame, people)

            # --- Rendering & Display ---
            canvas = ui.render(frame, people, recorder, fps, event_logger)
            cv2.imshow("Threat Detector", canvas)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()