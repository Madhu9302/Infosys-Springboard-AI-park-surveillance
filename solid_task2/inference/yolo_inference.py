from ultralytics import YOLO
import cv2
from inference.base_inference import BaseInference


class YOLOInference(BaseInference):
    """
    YOLO specific inference implementation
    """

    def __init__(self, model_path: str, conf: float = 0.4):
        self.model = YOLO(model_path)
        self.conf = conf

    def load_model(self):
        # Model already loaded in __init__
        return self.model

    def run_inference(self, video_path: str, output_path: str):
        cap = cv2.VideoCapture(video_path)

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = self.model(frame, conf=self.conf)

            annotated_frame = results[0].plot()
            out.write(annotated_frame)

        cap.release()
        out.release()
