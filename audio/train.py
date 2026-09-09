import json, os, torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score
from threat_detection.audio.dataset import SoundDataset
from threat_detection.audio.model import SoundCNN
from threat_detection.config import(
    SOUND_BATCH_SIZE,
    SOUND_LEARNING_RATE,
    SOUND_EPOCHS,
    SOUND_NUM_WORKERS,
    SOUND_TRAIN_DATASET_PATH,
    SOUND_VAL_DATASET_PATH,
    SOUND_WEIGHT_DECAY,
    SOUND_CLASSES
)

def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    predictions = []
    targets = []

    for inputs, labels in dataloader:
        inputs = inputs.to(device)
        labels = labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        predicted = torch.argmax(outputs, dim=1)
        predictions.extend(predicted.cpu().numpy())
        targets.extend(labels.cpu().numpy())
    
    epoch_loss = running_loss / len(dataloader)
    epoch_acc = accuracy_score(targets, predictions)

    return epoch_loss, epoch_acc

def validate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    predictions = []
    targets = []

    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            running_loss += loss.item()
            predicted = torch.argmax(outputs, dim=1)
            predictions.extend(predicted.cpu().numpy())
            targets.extend(labels.cpu().numpy())
    
    epoch_loss = running_loss / len(dataloader)
    epoch_acc = accuracy_score(targets, predictions)

    return epoch_loss, epoch_acc, predictions, targets


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device : {device}")

train_dataset = SoundDataset(SOUND_TRAIN_DATASET_PATH)
val_dataset = SoundDataset(SOUND_VAL_DATASET_PATH)
print(train_dataset.classes)
print(SOUND_CLASSES)

train_loader = DataLoader(
    train_dataset,
    batch_size = SOUND_BATCH_SIZE,
    shuffle=True,
    num_workers=SOUND_NUM_WORKERS,
    pin_memory=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=SOUND_BATCH_SIZE,
    shuffle=True,
    num_workers=SOUND_NUM_WORKERS,
    pin_memory=True
)

labels = [label for _, label in train_dataset.samples]
num_classes = len(train_dataset.classes)

class_counts = torch.bincount(
    torch.tensor(labels),
    minlength=num_classes
)

class_weights = class_counts.sum() / class_counts.float()
class_weights /= class_weights.sum()
class_weights = class_weights.to(device)

print("\nClass Weights :")

for cls, weight in zip(train_dataset.classes, class_weights):
    print(f"{cls:15s} : {weight:.4f}")
print()

model = SoundCNN(num_classes=num_classes).to(device)

criterion = nn.CrossEntropyLoss(weight=class_weights)

optimizer = optim.Adam(
    model.parameters(),
    lr=SOUND_LEARNING_RATE,
    weight_decay=SOUND_WEIGHT_DECAY
)

scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer=optimizer,
    mode="max",
    factor=0.5,
    patience=5
)

history = {
    "train_loss": [],
    "val_loss": [],
    "train_acc": [],
    "val_acc": [],
    "lr": []
}

best_accuracy = 0.0
best_epoch = 0

os.makedirs(r"D:\AI_Projects\threat_detection\audio\results", exist_ok=True)

for epoch in range(SOUND_EPOCHS):
    train_loss, train_acc = train_one_epoch(
        model,
        train_loader,
        criterion,
        optimizer,
        device
    )

    val_loss, val_acc, predictions, targets = validate(
        model,
        val_loader,
        criterion,
        device
    )

    scheduler.step(val_acc)
    current_lr = optimizer.param_groups[0]["lr"]

    history["train_loss"].append(train_loss)
    history["train_acc"].append(train_acc)

    history["val_loss"].append(val_loss)
    history["val_acc"].append(val_acc)

    history["lr"].append(current_lr)

    if val_acc > best_accuracy:
        best_accuracy = val_acc
        best_epoch = epoch + 1

        torch.save(model.state_dict(), r"D:\AI_Projects\threat_detection\audio\results\best_model.pth")

    print("=" * 60)        
    print(f"Epoch {epoch + 1}/{SOUND_EPOCHS}")
    print(f"Train Loss : {train_loss:.4f}")
    print(f"Train Accuracy : {train_acc*100:.2f}%")
    print(f"Val Loss : {val_loss:.4f}")
    print(f"Val Accuracy : {val_acc*100:.2f}%")
    print(f"Best Val : {best_accuracy*100:.2f}%")
    print(f"Learning Rate : {current_lr:.6f}")
    print("="*60)
    print()

    torch.save(model.state_dict(), r"D:\AI_Projects\threat_detection\audio\results\last_model.pth")
    
    with open(r"D:\AI_Projects\threat_detection\audio\results\history.json", "w") as file:
        json.dump(
            history,
            file,
            indent=4
        )
