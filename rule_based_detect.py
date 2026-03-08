from ultralytics import YOLO
import cv2

# 1️⃣ Load pretrained model
model = YOLO("best.pt")

# 2️⃣ Define rules
UNAUTHORIZED_OBJECTS = ["knife", "gun", "car", "truck", "bus", "motorcycle"]

def get_authorization(detected_classes):
    """
    detected_classes: list of class names detected in frame
    """
    for cls in detected_classes:
        if cls in UNAUTHORIZED_OBJECTS:
            return "UNAUTHORIZED"
    return "AUTHORIZED"


# 3️⃣ Run on webcam (change 0 to image/video if needed)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO inference
    results = model(frame)[0]

    detected_classes = []

    # Collect detected class names
    for box in results.boxes:
        cls_id = int(box.cls[0])
        class_name = model.names[cls_id]
        detected_classes.append(class_name)

    # 4️⃣ Apply rule-based logic
    status = get_authorization(detected_classes)

    # Draw YOLO boxes
    annotated_frame = results.plot()

    # Show final decision on frame
    color = (0, 255, 0) if status == "AUTHORIZED" else (0, 0, 255)
    cv2.putText(
        annotated_frame,
        f"STATUS: {status}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        3
    )

    cv2.imshow("Park Security - Rule Based", annotated_frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
