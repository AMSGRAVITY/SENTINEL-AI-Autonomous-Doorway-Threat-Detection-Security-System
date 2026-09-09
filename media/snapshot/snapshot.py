import os, cv2
from datetime import datetime
from threat_detection.config import SNAPSHOT_OUT_PATH

class SnapshotSaver:
    def __init__(self, output_dir = SNAPSHOT_OUT_PATH):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def capture(self, frame, prefix: str = "snapshot") -> str:

        if frame is None or frame.size == 0:
            print("[SNAPSHOT ERROR] Invalid or Empty frame provided !!!")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{prefix}_{timestamp}.jpg"
        filepath = os.path.abspath(os.path.join(self.output_dir, filename))

        success = cv2.imwrite(filepath, frame)

        if success:
            print(f"[SNAPSHOT] Saved Snapshot to: {filepath}")
            return filepath
        else:
            print(f"[SNAPSHOT ERROR] Failed to save snapshot to: {filepath}")
            return None