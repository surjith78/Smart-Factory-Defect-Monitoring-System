import cv2
import time
import json
import threading
import queue
import numpy as np
from datetime import datetime

# ==========================================
# Smart Factory Defect Monitoring System
# ==========================================

MAX_QUEUE_SIZE = 10
TOTAL_FRAMES = 500

frame_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
result_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)

# ==========================================
# DEFECT DETECTION
# ==========================================

def detect_defect(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = np.mean(gray)

    defect = (
        laplacian_var < 50 or
        brightness < 80 or
        brightness > 220
    )

    return defect, laplacian_var, brightness


# ==========================================
# SYNTHETIC FACTORY FRAME GENERATOR
# ==========================================

def create_factory_frame(frame_id):

    frame = np.full((360, 640, 3), 180, dtype=np.uint8)

    # conveyor belt
    cv2.rectangle(frame, (0, 120), (640, 260), (120, 120, 120), -1)

    # product
    cv2.rectangle(frame, (250, 140), (390, 240), (220, 220, 220), -1)

    is_defect = False

    # every 10th frame inject defect
    if frame_id % 10 == 0:

        defect_type = np.random.choice(
            ["hole", "scratch", "dark", "bright"]
        )

        is_defect = True

        if defect_type == "hole":
            cv2.circle(frame, (320, 190), 20, (0, 0, 0), -1)

        elif defect_type == "scratch":
            cv2.line(frame, (260, 150),
                     (380, 230), (0, 0, 0), 5)

        elif defect_type == "dark":
            frame[:] = 40

        elif defect_type == "bright":
            frame[:] = 255

    return frame, is_defect


# ==========================================
# PRODUCER THREAD
# ==========================================

def frame_producer():

    print("[PRODUCER] Generating frames...")

    for frame_id in range(TOTAL_FRAMES):

        frame, _ = create_factory_frame(frame_id)

        frame_queue.put((frame_id, frame))

        time.sleep(0.03)

    frame_queue.put(None)

    print("[PRODUCER] Finished")


# ==========================================
# CONSUMER THREAD
# ==========================================

def frame_consumer():

    defect_count = 0
    total_count = 0

    print("[CONSUMER] Started")

    while True:

        item = frame_queue.get()

        if item is None:
            result_queue.put(None)
            break

        frame_id, frame = item

        start_time = time.time()

        frame = cv2.resize(frame, (640, 360))

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

        processing_time = (
            time.time() - start_time
        ) * 1000

        # annotate image

        color = (0, 255, 0)

        if is_defect:
            color = (0, 0, 255)

        label = "DEFECT" if is_defect else "OK"

        cv2.putText(
            frame,
            label,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )

        cv2.putText(
            frame,
            f"Status: {status}",
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

        # save sample images
        if frame_id % 50 == 0:
            cv2.imwrite(
                f"sample_frame_{frame_id}.jpg",
                frame
            )

        log = {
            "timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            "frame_id": frame_id,
            "is_defect": bool(is_defect),
            "texture_score": round(float(texture), 2),
            "brightness": round(float(brightness), 2),
            "defect_rate": round(defect_rate, 3),
            "status": status,
            "processing_time_ms":
                round(processing_time, 2)
        }

        result_queue.put(log)

    print("[CONSUMER] Finished")


# ==========================================
# LOGGER THREAD
# ==========================================

def logger():

    print("[LOGGER] Started")

    with open(
        "factory_log.jsonl",
        "w"
    ) as logfile:

        while True:

            log = result_queue.get()

            if log is None:
                break

            logfile.write(
                json.dumps(log) + "\n"
            )

            logfile.flush()

            print(
    f"[LOG] {log['frame_id']} "
    f"{log['status']} "
    f"{log['defect_rate']}"
)

    print("[LOGGER] Finished")


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    print(
        "\n=== SMART FACTORY DEFECT "
        "MONITORING SYSTEM ===\n"
    )

    producer_thread = threading.Thread(
        target=frame_producer
    )

    consumer_thread = threading.Thread(
        target=frame_consumer
    )

    logger_thread = threading.Thread(
        target=logger
    )

    producer_thread.start()
    consumer_thread.start()
    logger_thread.start()

    producer_thread.join()
    consumer_thread.join()
    logger_thread.join()

    print("\nPipeline Completed Successfully!")

    print(
        "\nGenerated Files:"
    )

    print(
        "- factory_log.jsonl"
    )

    print(
        "- sample_frame_0.jpg"
    )

    print(
        "- sample_frame_50.jpg"
    )

    print(
        "- sample_frame_100.jpg ..."
    )