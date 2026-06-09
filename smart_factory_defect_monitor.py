import cv2
import time
import json
import threading
import queue
import numpy as np
from datetime import datetime

# ================================
# CONFIG
# ================================
VIDEO_SOURCE = 0  # webcam or "factory.mp4"
MAX_QUEUE_SIZE = 10

frame_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
result_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)

# ================================
# SIMPLE DEFECT DETECTOR (SIMULATION)
# ================================
def detect_defect(frame):
    """
    Simulated defect detection:
    - Uses brightness + noise + contour irregularity
    - No ML model required (fast + demo-friendly)
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Measure texture variation (proxy for defect)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Mean brightness
    brightness = np.mean(gray)

    # Rule-based defect logic
    defect_score = (laplacian_var < 80) or (brightness < 60 or brightness > 200)

    return defect_score, laplacian_var, brightness

# ================================
# PRODUCER THREAD
# ================================
def frame_producer():
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_queue.full():
            continue

        frame_queue.put((frame_id, frame))
        frame_id += 1

    cap.release()

# ================================
# CONSUMER THREAD
# ================================
def frame_consumer():
    defect_count = 0
    total_count = 0

    while True:
        if frame_queue.empty():
            continue

        frame_id, frame = frame_queue.get()
        start_time = time.time()

        # resize for speed
        frame = cv2.resize(frame, (640, 360))

        # detect defect
        is_defect, texture, brightness = detect_defect(frame)

        total_count += 1
        if is_defect:
            defect_count += 1

        defect_rate = defect_count / total_count

        status = "OK"
        if defect_rate > 0.15:
            status = "WARNING"
        if defect_rate > 0.30:
            status = "CRITICAL"

        processing_time = (time.time() - start_time) * 1000

        log = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "frame_id": frame_id,
            "is_defect": bool(is_defect),
            "texture_score": float(texture),
            "brightness": float(brightness),
            "defect_rate": round(defect_rate, 3),
            "status": status,
            "processing_time_ms": round(processing_time, 2)
        }

        result_queue.put(log)

        # Visualization
        label = "DEFECT" if is_defect else "OK"
        color = (0, 0, 255) if is_defect else (0, 255, 0)

        cv2.putText(frame, label, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.putText(frame, f"Status: {status}", (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Smart Factory Monitoring", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# ================================
# LOGGER THREAD
# ================================
def logger():
    with open("factory_log.jsonl", "w") as f:
        while True:
            if result_queue.empty():
                continue

            log = result_queue.get()
            f.write(json.dumps(log) + "\n")
            f.flush()

            print("[LOG]", log["frame_id"], log["status"], log["defect_rate"])

# ================================
# MAIN
# ================================
if __name__ == "__main__":
    print("[INFO] Starting Smart Factory Pipeline...")

    t1 = threading.Thread(target=frame_producer, daemon=True)
    t2 = threading.Thread(target=frame_consumer, daemon=True)
    t3 = threading.Thread(target=logger, daemon=True)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    cv2.destroyAllWindows()
