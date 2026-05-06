import cv2
import json
import time
import requests 
import numpy as np
import onnxruntime as ort
from insightface.app import FaceAnalysis

THINGSPEAK_API_KEY = ""  
THINGSPEAK_URL = ""

app = FaceAnalysis(name="buffalo_l", providers=["CUDAExecutionProvider"])
app.prepare(ctx_id=0, det_size=(640, 640))
raw = json.load(open("C:/Users/tunahan/Desktop/bitirmeProjesi/embeddings.json"))

db = {}
for name, poses in raw.items():
    emb_list = []
    for p in ["duz", "sag", "sol"]:
        if p in poses and poses[p]["mean_embedding"] is not None:
            emb_list.append(np.array(poses[p]["mean_embedding"]))
    if emb_list:
        db[name] = emb_list 

last_send_time = 0 
SEND_INTERVAL_SECONDS = 16

def send_to_thingspeak(person_name, similarity_score):
    global last_send_time
    current_time = time.time()
    
    if (current_time - last_send_time) < SEND_INTERVAL_SECONDS:
        print(f"[{person_name}] ThingSpeak gönderimi atlandı. {SEND_INTERVAL_SECONDS} saniye bekleniyor...")
        return

    safe_status = str(person_name)
    payload = {
        'api_key': THINGSPEAK_API_KEY,
        'status': f"{safe_status} - {int(time.time())}",
        'field2': float(similarity_score)
    }
    
    try:
        response = requests.post(THINGSPEAK_URL, data=payload, timeout=10)
        
        if response.status_code == 200 and response.text != '0':
            print(f"✅ ThingSpeak'e Gönderildi: {person_name} (Skor: {similarity_score:.2f})")
            last_send_time = current_time 
        else:
            print(f"❌ ThingSpeak Gönderim Hatası (HTTP Kodu: {response.status_code}, Yanıt: {response.text})")

    except requests.exceptions.RequestException as e:
        print(f"❌ Bağlantı Hatası: {e}")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kamera okunamıyor.")
        break

    faces = app.get(frame)

    for face in faces:
        x1, y1, x2, y2 = map(int, face.bbox)

        emb = face.normed_embedding
        emb_norm = np.linalg.norm(emb)
        best_name = "Bilinmiyor"
        best_sim = -1

        for name, pose_embs in db.items():
            for saved_emb in pose_embs:
                sim = np.dot(emb, saved_emb) / (emb_norm * np.linalg.norm(saved_emb))
                if sim > best_sim:
                    best_sim = sim
                    best_name = name

        if best_sim < 0.5:
            best_name = "Bilinmiyor"
            
        if best_name != "Bilinmiyor" and best_sim >= 0.5:
            send_to_thingspeak(best_name, best_sim)

        color = (0, 255, 0) if best_name != "Bilinmiyor" else (0, 0, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{best_name} ({best_sim:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow("Real Time Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
