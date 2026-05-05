import cv2

modelFile = "C:/Users/tunahan/Desktop/bitirmeProjesi/res10_300x300_ssd_iter_140000.caffemodel"
configFile = "C:/Users/tunahan/Desktop/bitirmeProjesi/deploy.prototxt"
net = cv2.dnn.readNetFromCaffe(configFile, modelFile)


yuzcas = cv2.CascadeClassifier("haarcascade_frontalface_default.xml.txt")


cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

    # --- Haar Cascade ---
    haar_frame = frame.copy()
    

    faces, rejectLevels, levelWeights = yuzcas.detectMultiScale3(haar_frame, scaleFactor=1.2, minNeighbors=5, outputRejectLevels=True)

    for (i, (x, y, w, h)) in enumerate(faces):
        cv2.rectangle(haar_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        conf = rejectLevels[i] 
        text = f"{conf:.2f}"
        cv2.putText(haar_frame, f"{conf:.2f}", (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    cv2.putText(haar_frame, "Haar Cascade", (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)
    dnn_frame = frame.copy()
    (h, w) = dnn_frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(dnn_frame, (300, 300)), 1.0,
                                 (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * [w, h, w, h]
            (x1, y1, x2, y2) = box.astype("int")
            cv2.rectangle(dnn_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            text = f"{confidence*100:.1f}%"
            cv2.putText(dnn_frame, text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(dnn_frame, "DNN Model", (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.imshow("Haar Cascade", haar_frame)
    cv2.imshow("DNN Model", dnn_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
