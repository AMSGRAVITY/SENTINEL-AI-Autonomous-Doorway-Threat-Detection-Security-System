import os, torch
import torch.nn.functional as F
from threat_detection.audio.feature_exctraction import FeatureExtraction
from threat_detection.audio.model import SoundCNN
from threat_detection.core.sound_event import SoundEvent
from threat_detection.config import (
    SOUND_REPORT_PATH,
    SOUND_CLASSES,
    SOUND_CLASSES_SCORES
)

class SoundClassifier:
    def __init__(self, model_path = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.extractor = FeatureExtraction()
        self.model = SoundCNN(len(SOUND_CLASSES)).to(self.device)

        if model_path is None:
            model_path = os.path.join(SOUND_REPORT_PATH, "best_model.pth")

        self.load_model(model_path)
        self.model.eval()

    def load_model(self, model_path):
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))

    def predict_prob(self, waveform, sample_rate):
        features = self.extractor.extract(waveform, sample_rate)

        features = features.unsqueeze(0)
        features = features.to(self.device)

        with torch.no_grad():
            outputs = self.model(features)
            prob = F.softmax(outputs, dim=1)

        return prob.squeeze(0)

    def get_sound_score(self, label):
        return SOUND_CLASSES_SCORES.get(label, 0)

    def predict(self, waveform, sample_rate):
        prob = self.predict_prob(waveform, sample_rate)
        conf, idx = torch.max(prob, dim=0)
        label = SOUND_CLASSES[idx.item()]

        event = SoundEvent()
        event.label = label
        event.confidence = float(conf.item())
        event.sound_score = self.get_sound_score(label)

        return event
