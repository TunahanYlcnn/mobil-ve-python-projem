import cv2
import time
import json
import serial
import numpy as np
import firebase_admin
from datetime import datetime
from insightface.app import FaceAnalysis
from firebase_admin import credentials, db as firebase_db

arduino = serial.Serial('COM6', 9600)
time.sleep(2)
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0, det_size=(640, 640))
cred = credentials.Certificate("C:/Users/tunahan/Desktop/bitirmeProjesi/akilliKapi.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://akillikapi-default-rtdb.firebaseio.com/"})

raw = json.load(open("C:/Users/tunahan/Desktop/bitirmeProjesi/embeddings.json"))
local_db = {}
for name, poses in raw.items():
    emb_list = []
    for p in ["duz", "sag", "sol"]:
        if p in poses and poses[p]["mean_embedding"] is not None:
            emb_list.append(np.array(poses[p]["mean_embedding"]))
    if emb_list:
        local_db[name] = emb_list 

cap = cv2.VideoCapture(0)

kapi_acik_mi = False
son_gorulme_zamani = 0 
bekleme_suresi = 5

while True:
    ret, frame = cap.read()
    if not ret:
        break

    kapi_acik_mi = firebase_db.reference("test_write6").get()

    if kapi_acik_mi == "door opened":
        if not kapi_acik_mi:
            arduino.write(b'1')
            kapi_acik_mi = True
    elif kapi_acik_mi == "door closed":
        if kapi_acik_mi:
            arduino.write(b'0')
            kapi_acik_mi = False

    faces = app.get(frame)
    su_an = time.time()
    
    kayitli_kisi_var_mi = False 
    taninan_kisi = ""
    en_yuksek_benzerlik = -1

    if len(faces) > 0:
        for face in faces:
            x1, y1, x2, y2 = map(int, face.bbox)
            emb = face.normed_embedding
            emb_norm = np.linalg.norm(emb)

            current_best_name = "Bilinmiyor"
            current_best_sim = -1
            
            for name, pose_embs in local_db.items():
                for saved_emb in pose_embs:
                    sim = np.dot(emb, saved_emb) / (emb_norm * np.linalg.norm(saved_emb))
                    if sim > current_best_sim:
                        current_best_sim = sim
                        current_best_name = name

            if current_best_sim < 0.5:
                current_best_name = "Bilinmiyor"
            else:
                kayitli_kisi_var_mi = True
                if current_best_sim > en_yuksek_benzerlik:
                    en_yuksek_benzerlik = current_best_sim
                    taninan_kisi = current_best_name

            renk = (0, 255, 0) if current_best_name != "Bilinmiyor" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), renk, 2)
            cv2.putText(frame, f"{current_best_name} ({current_best_sim:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, renk, 2)

        if kayitli_kisi_var_mi:
            son_gorulme_zamani = su_an
            if not kapi_acik_mi:
                kapi_acik_mi = True
                now = datetime.now()
                log_data = {
                    'person': taninan_kisi,
                    'accuracy': float(en_yuksek_benzerlik),
                    'date_time': now.strftime("%d.%m.%Y %H:%M:%S")
                }

                firebase_db.reference('test_write5').push(log_data)
                firebase_db.reference("test_write6").set("door opened")
                arduino.write(b'1')

    if not kayitli_kisi_var_mi and kapi_acik_mi:
        gecen_sure = su_an - son_gorulme_zamani
        if gecen_sure >= bekleme_suresi:
            firebase_db.reference("test_write6").set("door closed")
            arduino.write(b'0') 
            kapi_acik_mi = False
        else:
            kalan = int(bekleme_suresi - gecen_sure)
            cv2.putText(frame, f"Kapi kapaniyor: {kalan}s", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Akilli Kapi Sistemi", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()