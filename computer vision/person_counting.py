import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from threading import Thread, Lock
from scipy.spatial.distance import cosine

# --- CONFIGURATION ---
YOLO_MODEL = "yolov8n.pt"
CAM_SOURCES = [
    "rtsp://admin:admin%40123@192.168.1.104:554/cam/realmonitor?channel=1&subtype=0",
    "rtsp://admin:admin%40123@192.168.1.106:554/cam/realmonitor?channel=1&subtype=0"
]
FRAME_SIZE = (640, 480)
FRAME_SKIP = 2  # process every 2nd frame

# --- INITIALIZATION ---
model = YOLO(YOLO_MODEL)
trackers = [DeepSort(max_age=30) for _ in CAM_SOURCES]
lock = Lock()

# --- GLOBAL IDENTITY MANAGEMENT ---
global_persons = {}  # {global_id: embedding}
next_global_id = 1


class RTSPStream(Thread):
    def __init__(self, src, name="cam"):
        super().__init__(daemon=True)
        self.cap = cv2.VideoCapture(src)
        self.frame = None
        self.ret = False
        self.name = name
        self.stopped = False
        self.lock = Lock()
        self.start()

    def run(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.ret, self.frame = True, frame

    def read(self):
        with self.lock:
            if self.ret and self.frame is not None:
                return True, self.frame.copy()
            return False, None

    def release(self):
        self.stopped = True
        self.cap.release()


def match_global_identity(embedding):
    global global_persons, next_global_id
    if not global_persons:
        global_persons[next_global_id] = embedding
        next_global_id += 1
        return next_global_id - 1

    for gid, g_emb in global_persons.items():
        if cosine(embedding, g_emb) < 0.3:  # similarity threshold
            return gid

    global_persons[next_global_id] = embedding
    next_global_id += 1
    return next_global_id - 1


# --- START STREAMS ---
streams = [RTSPStream(src, name=f"cam{i+1}") for i, src in enumerate(CAM_SOURCES)]

frame_count = 0
while True:
    frames = []
    for s in streams:
        ret, frame = s.read()
        if ret:
            frame = cv2.resize(frame, FRAME_SIZE)
        else:
            frame = np.zeros((FRAME_SIZE[1], FRAME_SIZE[0], 3), dtype=np.uint8)
        frames.append(frame)

    frame_count += 1
    if frame_count % FRAME_SKIP != 0:
        continue

    for i, frame in enumerate(frames):
        results = model(frame, verbose=False)[0]
        detections = []
        for box in results.boxes:
            if int(box.cls[0]) == 0:  # person
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                detections.append(([x1, y1, x2 - x1, y2 - y1], conf, 'person'))

        tracks = trackers[i].update_tracks(detections, frame=frame)

        for t in tracks:
            if not t.is_confirmed():
                continue
            x1, y1, x2, y2 = map(int, t.to_ltrb())
            track_id = t.track_id
            embedding = t.last_detection.feature

            # Find or assign global ID
            global_id = match_global_identity(embedding)

            # Draw on frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"GID {global_id}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    total_unique = len(global_persons)
    combined = np.hstack(frames)
    cv2.putText(combined, f"Total Unique Persons: {total_unique}", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow("Multi-Camera Unique Person Counting", combined)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

for s in streams:
    s.release()
cv2.destroyAllWindows()
