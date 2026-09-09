import cv2
import os
import pickle
import numpy as np
from insightface.app import FaceAnalysis as FA

app = FA(name="buffalo_s", providers = ["CUDAExecutionProvider"])
app.prepare(ctx_id=0, det_size=(320, 320))

database = {}

dataset_path = "D:/AI_Projects/Face_Recognization/datasets"

for person in os.listdir(dataset_path):
    person_path = os.path.join(dataset_path, person)

    if not os.path.isdir(person_path):
        continue

    embeddings = []

    for img_name in os.listdir(person_path):
        img_path = os.path.join(person_path, img_name)

        image = cv2.imread(img_path)

        faces = app.get(image)

        if len(faces) == 0:
            continue

        embedding = faces[0].embedding
        embeddings.append(embedding)
    
    if len(embeddings) > 0:
        database[person] = np.mean(embeddings, axis=0)

with open("face_database.pkl", "wb") as f:
    pickle.dump(database, f)

print("Database saved!")