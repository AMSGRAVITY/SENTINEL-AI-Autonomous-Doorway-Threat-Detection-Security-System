import os, torch
import soundfile as sf
from torch.utils.data import Dataset
from threat_detection.audio.feature_exctraction import FeatureExtraction

class SoundDataset(Dataset):
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.samples = []
        self.classes = sorted([
            d for d in os.listdir(root_dir)
            if os.path.isdir(os.path.join(root_dir, d))
        ])
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}

        for cls in self.classes:
            class_dir = os.path.join(root_dir, cls)
            for file in os.listdir(class_dir):
                if file.endswith(".wav"):
                    self.samples.append((
                        os.path.join(class_dir, file),
                        self.class_to_idx[cls]
                    ))
        
        self.extractor = FeatureExtraction()
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        audio_path, label = self.samples[idx]
        waveform, sample_rate = sf.read(audio_path)

        waveform = torch.tensor(waveform, dtype=torch.float32)

        if waveform.ndim == 1:
            waveform = waveform.unsqueeze(0)
        else:
            waveform = waveform.transpose(0, 1)

        mel = self.extractor.extract(
            waveform=waveform,
            sample_rate=sample_rate
        )

        return mel, label