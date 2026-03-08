from ultralytics import YOLO
import cv2
import os

# --- SETTINGS ---
MODEL = YOLO("runs/detect/train/weights/best.pt")                    
INPUT_VIDEO = "videos/Road_traffic.mp4"  
OUTPUT_VIDEO = "outputs/output_detected.mp4"
CONF_THRESHOLD = 0.4

def main():
    # Check video exists
    if not os.path.exists(INPUT_VIDEO):
        raise FileNotFoundError(f"Video not found: {INPUT_VIDEO}")

    print("Loading YOLO 11s model...")
    model = YOLO(MODEL)  # Auto-download if not present

    cap = cv2.VideoCapture(INPUT_VIDEO)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, fps, (w, h))

    print("Processing video...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, conf=CONF_THRESHOLD)
        annotated = results[0].plot()
        out.write(annotated)

    cap.release()
    out.release()
    print("DONE! Output saved at:", OUTPUT_VIDEO)

if __name__ == "__main__":
    main()
