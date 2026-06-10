# Smart Factory Defect Monitoring System

---

##  Overview

This project is a **real-time Edge AI-inspired Smart Factory Monitoring System** designed to detect defective products in a simulated production line using video input.

The system implements a complete **data engineering pipeline** including:
- Real-time frame streaming
- Multi-threaded processing architecture
- Rule-based defect detection
- Dynamic risk assessment
- Structured JSON logging

It simulates how modern **Industry 4.0 smart factories** monitor product quality using AI and streaming data systems.

---

## Objectives

- Simulate real-time factory conveyor video stream (webcam or video file)
- Detect defective products using lightweight image analysis
- Compute real-time defect rate
- Classify system health status dynamically
- Log structured monitoring data in JSON format
- Demonstrate multi-threaded data pipeline architecture

---

## System Architecture

Frame Producer (Video Stream)
        ↓
Queue Buffer (Thread-safe Communication)
        ↓
Frame Consumer (Processing Engine)
        ↓
Defect Detection Module (Rule-based CV Logic)
        ↓
Risk Assessment Engine
        ↓
Logger Thread (JSON Storage + Console Output)
        ↓
Visualization Layer (OpenCV Display)

---

## Risk Assessment Logic

### OK
- defect rate ≤ 15%
- Normal production conditions

---

### WARNING
- defect rate > 15%
- Increasing number of defective products detected

---

### CRITICAL
- defect rate > 30%
- High probability of production failure or quality issue

---

## Sample Output

### Console Output

[INFO] Starting Smart Factory Pipeline...
[LOG] 12 OK 0.08
[LOG] 13 WARNING 0.18
[LOG] 14 CRITICAL 0.32

---

### JSON Log Entry (`factory_log.jsonl`)

{
  "timestamp": "2026-06-09 20:10:12",
  "frame_id": 14,
  "is_defect": true,
  "texture_score": 42.5,
  "brightness": 180.2,
  "defect_rate": 0.32,
  "status": "CRITICAL",
  "processing_time_ms": 18.4
}

---

### Visual Output
- Live video stream window
- Green label → OK product
- Red label → DEFECT product
- System status overlay (OK / WARNING / CRITICAL)

---

## Results

The system successfully:

- Processes real-time video stream using multi-threading
- Detects defects using lightweight computer vision logic
- Computes defect rate dynamically per frame
- Generates real-time risk classification
- Stores structured logs for analysis
- Provides live visual monitoring interface

This demonstrates a complete **end-to-end data engineering pipeline**.

---

## Technologies Used

- Python 3
- OpenCV
- NumPy
- Threading
- Queue (Producer–Consumer Model)
- JSON Logging
- datetime module

---

## Future Improvements

- Integration with YOLO-based defect detection
- MQTT-based cloud streaming for real-time monitoring
- Web dashboard using Streamlit or Flask
- Database storage (MongoDB / PostgreSQL)
- Predictive maintenance using time-series analysis
- Multi-camera factory monitoring system

---

## Author
Surjith Kumar Srinivasan Venkata(蘇吉特)
 614785078
Master's Program, Tamkang University


