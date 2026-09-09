import os, json, torch
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
    ConfusionMatrixDisplay
)
from torch.utils.data import DataLoader
from threat_detection.audio.dataset import SoundDataset
from threat_detection.audio.model import SoundCNN
from threat_detection.config import (
    SOUND_BATCH_SIZE,
    SOUND_NUM_WORKERS,
    SOUND_VAL_DATASET_PATH,
    SOUND_REPORT_PATH
)

def evaluate(model, dataloader):
    predictions = []
    targets = []

    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            predicted = torch.argmax(outputs, dim=1)
            predictions.extend(predicted.cpu().numpy())
            targets.extend(labels.numpy())

    return predictions, targets

def save_metrics_json(acc, prec, recall, f1):
    metrics = {
        "accuracy" : acc,
        "precision" : prec,
        "recall" : recall,
        "f1" : f1
    }

    with open(r"D:\AI_Projects\threat_detection\audio\results\metrics.json", "w") as file:
        json.dump(metrics, file, indent=4)

def save_classification_report(report):
    with open(r"D:\AI_Projects\threat_detection\audio\results\classification_report.txt", "w") as file:
        file.write(report)

def save_per_class_acc(targets, predictions, class_names):
    cm = confusion_matrix(targets, predictions)
    class_acc = {}

    print("\nPer-Class Accuracy : ")
    print("="*60)

    for i, class_name in enumerate(class_names):
        total = cm[i].sum()
        correct = cm[i][i]
        acc = correct / total if total > 0 else 0.0
        class_acc[class_name] = acc
        print(f"{class_name:15s} : {acc*100:.2f}%")
    print("="*60)

    with open(r"D:\AI_Projects\threat_detection\audio\results\per_class_accuracy.json", "w") as file:
        json.dump(class_acc, file, indent=4)

def save_confusion_matrix(targets, predictions, class_names):
    cm = confusion_matrix(targets, predictions)

    plt.figure(figsize=(8, 8))
    disp = ConfusionMatrixDisplay(confusion_matrix= cm, display_labels=class_names)
    disp.plot(cmap="Blues", values_format="d", colorbar=False)
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(os.path.join(SOUND_REPORT_PATH, "confusion_matrix.png"), dpi=300)
    plt.close()

def save_loss_curve(history):
    plt.figure(figsize=(8, 5))
    plt.plot(
        history["train_loss"],
        label = "Train Loss",
        linewidth = 2
    )
    plt.plot(
        history["val_loss"],
        label = "Validation Loss",
        linewidth = 2
    )
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Train vs Validation Loss Curve")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(SOUND_REPORT_PATH, "loss_curve.png"), dpi = 300)
    plt.close()

def save_acc_curve(history):
    plt.figure(figsize=(8, 5))
    plt.plot(
        history["train_acc"],
        label = "Train Accuracy",
        linewidth = 2
    )
    plt.plot(
        history["val_acc"],
        label = "Validation Accuracy",
        linewidth = 2
    )
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Train vs Validation Accuracy Curve")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(SOUND_REPORT_PATH, "acc_curve.png"), dpi = 300)
    plt.close()

#

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device : {device}\n")

val_dataset = SoundDataset(SOUND_VAL_DATASET_PATH)

val_loader = DataLoader(
    val_dataset,
    batch_size=SOUND_BATCH_SIZE,
    shuffle=False,
    num_workers=SOUND_NUM_WORKERS,
    pin_memory=True
)

model = SoundCNN(num_classes=len(val_dataset.classes)).to(device)

model.load_state_dict(
    torch.load(r"D:\AI_Projects\threat_detection\audio\results\best_model.pth", map_location=device)
)

model.eval()

predictions, targets = evaluate(model, val_loader)

accuracy = accuracy_score(targets, predictions)

precision, recall, f1, _ = precision_recall_fscore_support(
    targets,
    predictions,
    average="weighted",
    zero_division=0
)

with open(os.path.join(SOUND_REPORT_PATH, "history.json"), "r") as file:
    history = json.load(file)

print("Overall Metrics : ")
print("=" * 60)
print(f"Accuracy : {accuracy*100:.2f}%")
print(f"Precision : {precision*100:.2f}%")
print(f"Recall : {recall*100:.2f}%")
print(f"F1 Score : {f1*100:.2f}%")
print("=" * 60)

save_metrics_json(accuracy, precision, recall, f1)

report = classification_report(
    targets,
    predictions,
    target_names=val_dataset.classes,
    digits=4,
    zero_division=0
)

print(report)

save_classification_report(report)

save_per_class_acc(targets, predictions, val_dataset.classes)

save_confusion_matrix(targets, predictions, val_dataset.classes)

save_loss_curve(history)

save_acc_curve(history)