import time
from ultralytics import YOLO
from threat_detection.core.person_manager import PersonManager
from threat_detection.config import TRACKER_MODEL_PATH

class Tracker:
    def __init__(self, model_path = TRACKER_MODEL_PATH):
        self.model = YOLO(model_path)
        self.manager = PersonManager()
        self.max_missing_time = 2.0
    
    def update(self, frame):
        results = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=[0],
            verbose=False
        )

        current_tracks = set()
        current_time = time.time()

        if (
            len(results) == 0 
            or results[0].boxes is None
            or results[0].boxes.id is None
        ):
            self.cleanup(current_time)
            return self.manager.people
        
        boxes = results[0].boxes

        for box, track_id in zip(boxes.xyxy.cpu().numpy(), boxes.id.cpu().numpy()):
            track_id = int(track_id)
            current_tracks.add(track_id)
            person = self.manager.get_or_create(track_id)

            x1, y1, x2, y2 = map(float, box)
            person.bbox = (x1, y1, x2, y2)

            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            person.center = (cx, cy)
            person.center_history.append(((cx, cy), current_time))

            person.last_seen = current_time
            
            person.visible_time = person.last_seen - person.first_seen

        self.cleanup(current_time)

        return self.manager.people
    
    def cleanup(self, current_time):
        remove_ids = []

        for track_id, person in self.manager.people.items():
            if person.last_seen is None:
                continue

            if current_time - person.last_seen > self.max_missing_time:
                remove_ids.append(track_id)
        
        for track_id in remove_ids:
            self.manager.remove(track_id)