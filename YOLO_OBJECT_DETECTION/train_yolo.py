from ultralytics import YOLO

def main():
    # Load a model
    model = YOLO("yolo11s.pt")  # load a pretrained model (recommended for training)

    # Train the model
    results = model.train(data="local_data.yaml", epochs=100, imgsz=640)

if __name__ == '__main__':
    main()
