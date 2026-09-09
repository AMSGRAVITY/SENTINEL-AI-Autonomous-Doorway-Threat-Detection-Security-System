import cv2
import numpy as np
from ultralytics import YOLO
from threat_detection.config import WEAPON_MODEL_PATH, WEAPON_CONF_THRESH
from threat_detection.core.person_track import PersonTrack

LARGE_WEAPON_CLASSES = {"automatic_rifle", "shotgun", "smg", "sniper", "bazooka", "grenade_launcher", "sword"}

class WeaponDetector:
    def __init__(self, model_path=WEAPON_MODEL_PATH, conf_thresh=WEAPON_CONF_THRESH):
        self.model = YOLO(model_path)
        self.conf_thresh = conf_thresh

    def update(self, frame, people: dict):
        if not people:
            return people

        # Store candidate detections for current frame per person ID
        person_candidates = {pid: [] for pid in people.keys()}

        results = self.model.predict(frame, conf=self.conf_thresh, verbose=False)

        if results and results[0].boxes is not None and len(results[0].boxes) > 0:
            names_dict = results[0].names

            for box, conf, cls_id in zip(
                results[0].boxes.xyxy.cpu().numpy(),
                results[0].boxes.conf.cpu().numpy(),
                results[0].boxes.cls.cpu().numpy()
            ):
                wx1, wy1, wx2, wy2 = map(float, box)
                w_w = wx2 - wx1
                w_h = wy2 - wy1
                w_center_x = (wx1 + wx2) / 2.0
                w_center_y = (wy1 + wy2) / 2.0
                conf_val = float(conf)
                cls_id = int(cls_id)
                weapon_name = str(names_dict.get(cls_id, 'weapon'))

                print("WEAPON :", weapon_name)

                # RULE 3: Physical Bounding Box Size Sanity Check
                # Large long-guns (AR, shotgun, etc.) must satisfy minimum dimensions
                if weapon_name in LARGE_WEAPON_CLASSES:
                    if w_w < 45 or w_h < 45 or (w_w * w_h) < 2000:
                        continue  # Rejects small false positives (like phones misclassified as AR)
                else:
                    if w_w < 15 or w_h < 15:
                        continue

                # Spatial association with tracked people
                for pid, person in people.items():
                    px1, py1, px2, py2 = map(float, person.bbox)
                    p_height = py2 - py1

                    # RULE 2: Head / Upper Face Exclusion Zone
                    # Weapons are held by hand/arm zone, NOT on top of upper face/head
                    upper_head_cutoff = py1 + 0.25 * p_height
                    if w_center_y <= upper_head_cutoff:
                        continue

                    # Expand body box slightly for hand reach zone (from chest down)
                    exp_px1 = px1 - 35.0
                    exp_py1 = py1 - 10.0
                    exp_px2 = px2 + 35.0
                    exp_py2 = py2 + 50.0

                    if (exp_px1 <= w_center_x <= exp_px2) and (exp_py1 <= w_center_y <= exp_py2):
                        person_candidates[pid].append((weapon_name, conf_val, (int(wx1), int(wy1), int(wx2), int(wy2))))

        # RULE 4: Multi-Frame Temporal Persistence Filter (2-Frame Confirmation)
        for pid, person in people.items():
            candidates = person_candidates.get(pid, [])
            if candidates:
                person.weapon_candidate_count += 1
            else:
                person.weapon_candidate_count = max(0, person.weapon_candidate_count - 1)

            # Trigger weapon_detected ONLY when confirmed across 2 consecutive analysis frames
            if person.weapon_candidate_count >= 2 and candidates:
                person.weapon_detected = True
                person.detected_weapons = []
                person.weapon_boxes = []
                max_conf = 0.0
                for w_name, conf_val, wbox in candidates:
                    if w_name not in person.detected_weapons:
                        person.detected_weapons.append(w_name)
                    person.weapon_boxes.append(wbox)
                    max_conf = max(max_conf, conf_val)
                person.weapon_confidence = max_conf
            else:
                person.weapon_detected = False
                person.detected_weapons = []
                person.weapon_boxes = []
                person.weapon_confidence = 0.0

        return people

