from ultralytics import YOLO

# Load pretrained classification model
model = YOLO("yolo11n-cls.pt")

model.train(
    data=r"D:\AI_Projects\threat_detection\mask\dataset",
    epochs=30,
    imgsz=224,
    batch=32,
    workers=0,
    device=0,
    optimizer="AdamW",
    lr0=1e-3,
    weight_decay=5e-4,
    patience=10,
    pretrained=True,
    verbose=True,
    project=r"D:\AI_Projects\threat_detection\mask\runs",
    name="mask_classifier"
)

metrics = model.val()

print("\nTraining Finished")
print(metrics)