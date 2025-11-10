from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2
import numpy as np
from threading import Thread, Lock
from scipy.spatial.distance import cosine

# ------------------------
# CONFIGURATION
# ------------------------
model = YOLO("yolov8n.pt")  # small YOLOv8 model
cam1_url = "rtsp://admin:admin%40123@192.168.1.104:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif"
cam2_url = "rtsp://admin:admin%40123@192.168.1.106:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif"
resize_dim = (640, 480)
EMBED_THRESHOLD = 0.4  # cosine distance threshold for same person

# ------------------------
# RTSP Stream Handling
# ------------------------
class RTSPStream:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        self.ret, self.frame = self.cap.read()
        self.lock = Lock()
        self.stopped = False
        Thread(target=self.update, daemon=True).start()

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.ret = ret
                    self.frame = frame

    def read(self):
        with self.lock:
            if self.ret and self.frame is not None:
                return True, self.frame.copy()
            else:
                return False, None

    def release(self):
        self.stopped = True
        self.cap.release()

# ------------------------
# INITIALIZE STREAMS AND TRACKERS
# ------------------------
stream1 = RTSPStream(cam1_url)
stream2 = RTSPStream(cam2_url)
tracker1 = DeepSort(max_age=30)
tracker2 = DeepSort(max_age=30)

# Global embeddings to maintain unique person count
global_embeddings = []

def is_new_person(embedding):
    """Check if embedding is new compared to global embeddings"""
    for e in global_embeddings:
        if cosine(embedding, e) < EMBED_THRESHOLD:
            return False
    return True

def add_embedding(embedding):
    global_embeddings.append(embedding)

# ------------------------
# MAIN LOOP
# ------------------------
while True:
    frames = []
    for stream in [stream1, stream2]:
        ret, frame = stream.read()
        if ret:
            frame = cv2.resize(frame, resize_dim)
            frames.append(frame)
        else:
            frames.append(np.zeros((resize_dim[1], resize_dim[0], 3), dtype=np.uint8))

    # Detect persons in each frame
    results1 = model(frames[0], verbose=False)[0]
    dets1 = []
    for box in results1.boxes:
        if int(box.cls[0]) == 0:  # person class
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            dets1.append(([x1, y1, x2-x1, y2-y1], conf, "person"))

    results2 = model(frames[1], verbose=False)[0]
    dets2 = []
    for box in results2.boxes:
        if int(box.cls[0]) == 0:  # person class
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            dets2.append(([x1, y1, x2-x1, y2-y1], conf, "person"))

    # Update trackers
    tracks1 = tracker1.update_tracks(dets1, frame=frames[0])
    tracks2 = tracker2.update_tracks(dets2, frame=frames[1])

    # Update global embeddings and count unique persons
    for tracks in [tracks1, tracks2]:
        for t in tracks:
            if not t.is_confirmed():
                continue
            if t.last_embedding is not None:
                if is_new_person(t.last_embedding):
                    add_embedding(t.last_embedding)

    # Draw bounding boxes and IDs
    for frame, tracks in zip(frames, [tracks1, tracks2]):
        for t in tracks:
            if not t.is_confirmed():
                continue
            x1, y1, x2, y2 = map(int, t.to_ltrb())
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID {t.track_id}", (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Show unique person count on first frame
    cv2.putText(frames[0], f"Unique Persons: {len(global_embeddings)}", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    # Combine frames side by side with a small gap
    gap = 20
    gap_strip = np.zeros((resize_dim[1], gap, 3), dtype=np.uint8)
    combined = np.hstack([frames[0], gap_strip, frames[1]])

    cv2.imshow("Unique Person Counting", combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ------------------------
# CLEANUP
# ------------------------
stream1.release()
stream2.release()
cv2.destroyAllWindows()
