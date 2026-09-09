import os
import soundfile as sf

INPUT_FOLDER = r"D:\AI_Projects\threat_detection\recordings\WAV"
OUTPUT_FOLDER = r"D:\AI_Projects\threat_detection\silence"

CLIP_DURATION = 3  # seconds

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for filename in os.listdir(INPUT_FOLDER):

    if not filename.endswith(".wav"):
        continue

    path = os.path.join(INPUT_FOLDER, filename)

    audio, sr = sf.read(path)

    samples_per_clip = CLIP_DURATION * sr

    total_clips = len(audio) // samples_per_clip

    base = os.path.splitext(filename)[0]

    for i in range(total_clips):

        start = i * samples_per_clip
        end = start + samples_per_clip

        clip = audio[start:end]

        out_name = f"{base}_{i:03d}.wav"

        sf.write(
            os.path.join(OUTPUT_FOLDER, out_name),
            clip,
            sr
        )

print("Done!")