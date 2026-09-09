from threat_detection.audio.recorder import Recorder
from threat_detection.audio.classifier import SoundClassifier
from threat_detection.config import SOUND_CLASSES


def main():

    recorder = Recorder()

    classifier = SoundClassifier()

    print("Starting Recorder...")

    recorder.start()

    input("\nPress ENTER to record...")

    print("Recording...")

    waveform, sample_rate = recorder.record()

    recorder.stop()

    recorder.save(r"D:\AI_Projects\threat_detection\audio\live.wav")

   # waveform, sample_rate = recorder.load(r"D:\AI_Projects\threat_detection\audio\200460-6-1-0.wav")
    print(sample_rate)
    print(f"Waveform shape : {waveform.shape}")
    print(f"Min and max : {waveform.min(), waveform.max()}")

    print("\nPredicting...\n")

    probs = classifier.predict_prob(waveform, sample_rate)

    for cls, p in zip(SOUND_CLASSES, probs):
        print(f"{cls:12} : {p.item()*100:.2f}%")

    event = classifier.predict(waveform, sample_rate)

    print("=" * 40)
    print(f"Label      : {event.label}")
    print(f"Confidence : {event.confidence:.2%}")
    print(f"Score      : {event.sound_score}")
    print("=" * 40)


if __name__ == "__main__":
    main()