import torch
import torchaudio
from torchvision.transforms import Resize
from threat_detection.audio.model import NUM_MELS, INPUT_SIZE
from threat_detection.config import(
    SAMPLE_RATE,
    N_FFT,
    HOP_LENGTH
)

class FeatureExtraction:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.mel_transform = torchaudio.transforms.MelSpectrogram(
            sample_rate=SAMPLE_RATE,
            n_fft=N_FFT,
            hop_length=HOP_LENGTH,
            n_mels=NUM_MELS
        )
        self.resize = Resize(INPUT_SIZE)

    def extract(self, waveform, sample_rate):
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        
        if sample_rate != 22050:
            waveform = torchaudio.functional.resample(waveform, sample_rate, SAMPLE_RATE)
        
        mel = self.mel_transform(waveform)

        mel = torch.log(mel + 1e-9)

        mel = (mel - mel.mean()) / (mel.std() + 1e-9)

        mel = self.resize(mel)

        return mel