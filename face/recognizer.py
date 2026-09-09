import pickle
import math
import numpy as np
from insightface.app import FaceAnalysis as FA
from threat_detection.config import (
    IOU_DIST_RATIO,
    FACE_DATABSE_PATH
)

class FaceRecognizer:
    def __init__(
            self,
            database_path = FACE_DATABSE_PATH,
            model_name="buffalo_s",
            providers=["CUDAExecutionProvider"],
            thresh = 0.4
    ):
        self.thresh = thresh
        self.app = FA(name=model_name, providers=providers)
        self.app.prepare(ctx_id=0, det_size=(320,320))
        with open(database_path, "rb") as f:
            self.database = pickle.load(f)
    
    def cosine_similarity(self, emb1, emb2):
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    
    def iou(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        inter_w = max(0, xB - xA)
        inter_h = max(0, yB - yA)
        inter_area = inter_w * inter_h

        if inter_area == 0:
            return 0
        
        areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        return inter_area / (areaA + areaB - inter_area)
    
    def find_person(self, face_box, people):
        best_person = None
        best_score = 0

        for person in people.values():
            if person.bbox is None:
                continue

            iou_score = self.iou(face_box, person.bbox)
            distance_score = self.center_distance_score(face_box, person)

            score = IOU_DIST_RATIO * iou_score + (1 - IOU_DIST_RATIO) * distance_score

            if score > best_score:
                best_score = score
                best_person = person
        
        return best_person
    
    def center_distance_score(self, face_box, person):
        if person.center is None:
            return 0
        
        cx = (face_box[0] + face_box[2]) / 2
        cy = (face_box[1] + face_box[3]) / 2

        dx = cx - person.center[0]
        dy = cy - person.center[1]

        distance = math.sqrt(dx*dx + dy*dy)

        x1, y1, x2, y2 = person.bbox

        body_width = max(x2 - x1, 1)

        score = 1 - (distance / body_width)

        return max(0, min(score, 1))
    
    def update(self, frame, people):
        for person in people.values():
            person.has_face = False
            person.face = None
            person.face_bbox = None
            person.face_landmarks = None
            person.face_embeddings = None
        
        faces = self.app.get(frame)

        for face in faces:
            face_box = tuple(face.bbox.tolist())
            person = self.find_person(face_box, people)

            if person is None:
                continue

            person.has_face = True
            person.face = face
            person.face_bbox = face_box
            person.face_landmarks = face.kps
            person.face_embeddings = face.embedding

            best_name = "Unknown"
            best_score = -1

            for name, embd in self.database.items():
                score = self.cosine_similarity(face.embedding, embd)
                
                if score > best_score:
                    best_name = name
                    best_score = score
            
            if best_score < self.thresh:
                best_name = "Unknown"
            
            person.identity = best_name
            person.face_match_score = best_score

        return people