from ultralytics import YOLO
from threat_detection.core.person_track import PersonTrack
from threat_detection.config import MASKED_MODEL_PATH

class MaskDetector:

    def __init__(self, model_path = MASKED_MODEL_PATH):

        self.model = YOLO(model_path)

    def update(self, frame, person: PersonTrack):

        person.masked = False
        person.mask_confidence = 0.0

        if not person.has_face:
            return person

        if person.face_bbox is None:
            return person

        x1, y1, x2, y2 = map(int, person.face_bbox)

        h, w = frame.shape[:2]

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)

        if x2 <= x1 or y2 <= y1:
            return person

        face_crop = frame[y1:y2, x1:x2]

        if face_crop.size == 0:
            return person

        result = self.model(face_crop, verbose=False)[0]

        if result.probs is None:
            return person

        class_id = result.probs.top1

        confidence = float(result.probs.top1conf)

        class_name = result.names[class_id]

        person.mask_confidence = confidence

        person.masked = (class_name == "with_mask")

        return person