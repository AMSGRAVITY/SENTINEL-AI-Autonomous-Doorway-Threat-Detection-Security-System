import os, torch
import numpy as np
import sounddevice as sd
import soundfile as sf
from threat_detection.config import (
    SAMPLE_RATE,
    AUDIO_CHANNELS,
    AUDIO_CHUNK_DURATION,
    AUDIO_DTYPE
)

class Recorder:
    def __init__(
            self,
            sample_rate = SAMPLE_RATE,
            channels = AUDIO_CHANNELS,
            dtype = AUDIO_DTYPE,
            chunk_dur = AUDIO_CHUNK_DURATION
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.chunk_dur = chunk_dur
        self.recording = False
        self.waveform = None

    def start(self):
        self.recording = True

    def stop(self):
        self.recording = False

    def is_recording(self):
        return self.recording

    def record(self):
        if not self.is_recording:
            raise RuntimeError("Recording has not been started")

        samples = int(self.sample_rate * self.chunk_dur)
        audio = sd.rec(
            samples,
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype
        )

        sd.wait()
        print("AUDIO : ")
        print(audio.dtype)
        print(audio.min())
        print(audio.max())

        if self.channels > 1:
            audio = np.mean(audio, axis=1, keepdims=True)

        audio = torch.from_numpy(audio).float().T

        self.waveform = audio
        return audio, self.sample_rate

    def save(self, filename):
        if self.waveform is None:
            raise ValueError("No Recording is available")

        os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None

        waveform = self.waveform.squeeze(0).numpy()

        sf.write(filename, waveform, self.sample_rate)

    def load(self, filename):
        waveform, sample_rate = sf.read(filename, dtype=self.dtype)

        if waveform.ndim > 1:
            waveform = waveform.mean(axis=1)

        waveform = torch.from_numpy(waveform).float()

        waveform = waveform.unsqueeze(0)

        self.waveform = waveform
        self.sample_rate = sample_rate

        return waveform, sample_rate

    def clear(self):
        self.waveform = None