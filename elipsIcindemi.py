import cv2
import numpy as np
from insightface.app import FaceAnalysis

app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0, det_size=(640, 640))

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    if not ret:
        break

    h, w = frame.shape[:2]
    cx, cy = w//2, h//2
    ell_w, ell_h = int(w*0.25), int(h*0.35)

    # Elips çiz (referans alan)
    cv2.ellipse(frame, (cx, cy), (ell_w, ell_h), 0, 0, 360, (0, 0, 255), 2)

    faces = app.get(frame)
    if faces:
        kps = np.asarray(faces[0].kps)
        nose = tuple(kps[2][:2].astype(int))
        cv2.circle(frame, nose, 4, (0,255,0), -1)

        # Burun elipsin içinde mi?
        nx, ny = nose
        inside = ((nx-cx)**2)/(ell_w**2) + ((ny-cy)**2)/(ell_h**2) <= 1

        if inside:
            cv2.ellipse(frame, (cx, cy), (ell_w, ell_h), 0, 0, 360, (0, 255, 0), 2)


    cv2.imshow("Cam", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
