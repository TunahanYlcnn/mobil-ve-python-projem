import cv2, numpy as np, math, time, json, os
from insightface.app import FaceAnalysis

ctx_id = 0 
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=ctx_id, det_size=(640, 640))

PERSON = "tunahan"
poses = ["duz", "sag", "sol"]

data = {p: [] for p in poses}
cur = 0
stable_count = 0
prev_nose = None
yaw_hist = []
last_cap_time = 0.0

def rot_euler(R):
    sy = math.sqrt(R[0,0]**2 + R[1,0]**2)
    if sy < 1e-6:
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0.0
    else:
        x = math.atan2(R[2,1], R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    return np.degrees([x, y, z])

def head_pose(kps, h, w):

    pts = np.array([
        kps[2],            
        kps[0],           
        kps[1],           
        kps[3],           
        kps[4],           
        (kps[3] + kps[4]) / 2.0  
    ], dtype=np.float64)

    mdl = np.array([
        (0.0, 0.0, 0.0),
        (-30.0, -65.0, -30.0),
        (30.0, -65.0, -30.0),
        (-50.0, -95.0, -35.0),
        (50.0, -95.0, -35.0),
        (0.0, -95.0, -30.0)
    ], dtype=np.float64)

    focal = w  # kabaca
    cam = np.array([[focal, 0.0, w / 2.0],
                    [0.0, focal, h / 2.0],
                    [0.0, 0.0, 1.0]], dtype=np.float64)

    dist = np.zeros((4, 1), dtype=np.float64)

    try:
        retval, rvec, tvec = cv2.solvePnP(mdl, pts, cam, dist, flags=cv2.SOLVEPNP_ITERATIVE)
    except Exception:
        return None


    if retval is None or (isinstance(retval, (bool, np.bool_)) and retval is False):
        return None

    rmat, _ = cv2.Rodrigues(rvec)
    yaw = rot_euler(rmat)[1]
    return {"yaw": float(yaw)}

def centered(box, w, h, t=0.18):
    x1, y1, x2, y2 = box
    bx, by = (x1 + x2) / 2.0, (y1 + y2) / 2.0
    return abs(bx - w / 2.0) < w * t and abs(by - h / 2.0) < h * t

def label_pose(p):
    yaw = p["yaw"]
    if abs(yaw) < 15:
        return "duz"
    return "sag" if yaw > 0 else "sol"

def inside_ellipse(pt, cx, cy, rx, ry):
    x, y = pt
    return ((x - cx) ** 2) / (rx ** 2) + ((y - cy) ** 2) / (ry ** 2) <= 1.0


cap = cv2.VideoCapture(0)

while cur < len(poses):
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    if not ret:
        break

    h, w = frame.shape[:2]
    target_pose = poses[cur]

    ellipse_color = (0, 0, 255)

    faces = app.get(frame)
    pose_label = "Yuz yok"
    pose_color = (0, 0, 255)

    if faces and len(faces) > 0 and getattr(faces[0], "det_score", 1.0) > 0.6:
        face = faces[0]
        kps = np.array(face.kps)[:,:2]
        x1, y1 = int(kps[:,0].min()), int(kps[:,1].min())
        x2, y2 = int(kps[:,0].max()), int(kps[:,1].max())

        cx, cy = w // 2, h // 2
        rx, ry = 120, 160

        landmarks = [tuple(p.astype(int)) for p in kps]
        is_center = all(inside_ellipse(pt, cx, cy, rx, ry) for pt in landmarks)

        ellipse_color = (0,255,0) if is_center else (0,0,255)

        if is_center:
            hp = head_pose(kps, h, w)
            if hp is not None:
                yaw_hist.append(hp["yaw"])

                yaw_hist = yaw_hist[-3:]
                hp["yaw"] = float(yaw_hist[-1])  

                detected = label_pose(hp)

                if detected == target_pose:
                    pose_label = target_pose.upper()
                    pose_color = (0,255,0)
                else:
                    if target_pose == "duz":
                        pose_label = "Yuzu ortala ve duz dur"
                    elif target_pose == "sag":
                        pose_label = "Yuzu ortala ve saga don"
                    elif target_pose == "sol":
                        pose_label = "Yuzu ortala ve sola don"
                    pose_color = (0,0,255)

                nose = tuple(kps[2].astype(int))

                stable_pos = prev_nose is None or math.dist(nose, prev_nose) < 16
                prev_nose = nose


                emb = None
                for attr in ("normed_embedding", "embedding", "feat", "repr"):
                    if hasattr(face, attr):
                        val = getattr(face, attr)
                        if isinstance(val, (np.ndarray, list, tuple)):
                            emb = np.array(val, dtype=float).flatten()
                            break

                if stable_pos and detected == target_pose and emb is not None:
                    stable_count += 1
                    if stable_count >= 4 and time.time() - last_cap_time > 0.02:
                        data[target_pose].append(emb.tolist())
                        last_cap_time = time.time()
                        stable_count = 0
                else:
                    stable_count = 0
            else:
                stable_count = 0
        else:
            pose_label = "Yuzu ortala"
            pose_color = (0,0,255)
            stable_count = 0
    else:
        stable_count = 0
        prev_nose = None


    cv2.ellipse(frame, (w//2, h//2), (120,160), 0, 0, 360, ellipse_color, 1)
    cv2.putText(frame, f"{target_pose.upper()} {len(data[target_pose])}/{20}", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
    cv2.putText(frame, pose_label, (20,90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, pose_color, 2)

    cv2.imshow("Cam", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    if len(data[target_pose]) >= 20:
        cur += 1
        stable_count = 0
        prev_nose = None
        yaw_hist.clear()
        time.sleep(0.2)

cap.release()
cv2.destroyAllWindows()


db_path = "embeddings.json"
db = {}
if os.path.exists(db_path):
    try:
        db = json.load(open(db_path, "r"))
    except Exception:
        db = {}


db[PERSON] = {}
for p in poses:
    if data[p]:
        arr = np.array(data[p], dtype=float)
        mean_emb = arr.mean(axis=0).tolist()
        db[PERSON][p] = {"mean_embedding": mean_emb, "n_samples": int(arr.shape[0])}
    else:
        db[PERSON][p] = {"mean_embedding": None, "n_samples": 0}

with open(db_path, "w") as f:
    json.dump(db, f, indent=2)

print("Kaydedildi ✅")
