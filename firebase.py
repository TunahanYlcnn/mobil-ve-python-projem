import firebase_admin
from firebase_admin import credentials, db as firebase_db
import cv2
import json
import numpy as np
from insightface.app import FaceAnalysis
import time

app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0, det_size=(640, 640))

raw = json.load(open("C:/Users/tunahan/Desktop/bitirmeProjesi/embeddings.json"))

cred = credentials.Certificate("C:/Users/tunahan/Desktop/bitirmeProjesi/akilliKapi.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": ""})

local_db = {}
for name, poses in raw.items():
    emb_list = []
    for p in ["duz", "sag", "sol"]:
        if p in poses and poses[p]["mean_embedding"] is not None:
            emb_list.append(np.array(poses[p]["mean_embedding"]))
    if emb_list:
        local_db[name] = emb_list 

cap = cv2.VideoCapture(0)

face_detected_sent = False   

while True:
    ret, frame = cap.read()
    faces = app.get(frame)

    if len(faces) > 0:
        for face in faces:
            x1, y1, x2, y2 = map(int, face.bbox)

            emb = face.normed_embedding
            emb_norm = np.linalg.norm(emb)

            best_name = "Bilinmiyor"
            best_sim = -1

            # Embedding karşılaştır
            for name, pose_embs in local_db.items():
                for saved_emb in pose_embs:
                    sim = np.dot(emb, saved_emb) / (emb_norm * np.linalg.norm(saved_emb))
                    if sim > best_sim:
                        best_sim = sim
                        best_name = name

            if best_sim < 0.5:
                best_name = "Bilinmiyor"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{best_name} ({best_sim:.2f})",
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 255, 0), 2)
            
            if not face_detected_sent:
                data = {
                    'kişi': best_name,
                    'doğruluk': best_sim}
                
                firebase_db.reference('detected_face').push(data)
                print("Firebase'e gönderildi: yüz algılandı")
                face_detected_sent = True

    else:
        face_detected_sent = False

    cv2.imshow("Gerçek Zamanlı Tanıma", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
