from ultralytics import YOLO

model = YOLO("yolov8s.pt")

print("Started!!!")
model.train(
    data = r"D:\AI_Projects\threat_detection\tracking\Motion_Detection\datasets\data.yaml",
    epochs = 100,
    imgsz = 640,
    batch = 16,
    device = 0,
    workers = 0,
    patience = 20,
    project = r"D:\AI_Projects\threat_detection\weapons",
    name = "metrics"
)
