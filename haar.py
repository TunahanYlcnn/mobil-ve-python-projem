import cv2

yuzcas = cv2.CascadeClassifier("haarcascade_frontalface_default.xml.txt")
cam = cv2.VideoCapture(0)

while True:
    ret, frame = cam.read()
    frame = cv2.flip(frame, 1) 
    faces = yuzcas.detectMultiScale(frame, 1.2, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x - 20, y - 20), (x + w + 20, y + h + 20), (0, 255, 0), 3)
        cv2.putText(frame, "tespit", (x - 20, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Yuz Tanima', frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
