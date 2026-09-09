from pathlib import Path
import random
import librosa
import numpy as np
import soundfile as sf


def add_background_noise(
    clean_audio: np.ndarray, noise_audio: np.ndarray, snr_db: float
) -> np.ndarray:
    """Overlays noise_audio onto clean_audio at a target SNR (in dB) using NumPy/librosa."""
    clean_len = len(clean_audio)
    noise_len = len(noise_audio)

    # 1. Match lengths (crop or pad noise to fit clean audio length)
    if noise_len < clean_len:
        # Repeat noise if it's shorter than the clean clip
        repeats = (clean_len // noise_len) + 1
        noise_audio = np.tile(noise_audio, repeats)[:clean_len]
    elif noise_len > clean_len:
        # Random crop if noise is longer than clean clip
        start = random.randint(0, noise_len - clean_len)
        noise_audio = noise_audio[start : start + clean_len]

    # 2. Calculate RMS (Root Mean Square) energy
    clean_power = np.mean(clean_audio**2)
    noise_power = np.mean(noise_audio**2)

    # Handle dead silence to avoid division by zero
    if noise_power == 0 or clean_power == 0:
        return clean_audio

    # 3. Scale noise to match requested Signal-to-Noise Ratio (SNR)
    # Formula: SNR = 10 * log10(P_clean / P_noise) => P_noise_target = P_clean / (10^(SNR/10))
    snr_factor = 10 ** (snr_db / 10.0)
    target_noise_power = clean_power / snr_factor
    scale = np.sqrt(target_noise_power / (noise_power + 1e-8))

    scaled_noise = noise_audio * scale

    # 4. Mix signals and clip values between -1.0 and 1.0 to prevent distortion
    noisy_audio = clean_audio + scaled_noise
    noisy_audio = np.clip(noisy_audio, -1.0, 1.0)

    return noisy_audio


def augment_dataset(
    dataset_dir: str,
    silence_dir: str,
    output_dir: str,
    classes_to_augment: list[str],
    num_augmented_per_file: int = 1,
    snr_range: tuple[float, float] = (5.0, 20.0),
    target_sr: int = 44100,
):
    """Iterates over specified audio classes and generates noisy versions using librosa & soundfile."""
    dataset_path = Path(dataset_dir)
    silence_files = list(Path(silence_dir).glob("*.wav"))

    if not silence_files:
        raise FileNotFoundError(f"No WAV files found in '{silence_dir}'")

    print(f"Found {len(silence_files)} silence/background noise files.")

    for class_name in classes_to_augment:
        class_folder = dataset_path / class_name
        if not class_folder.exists():
            print(f"Warning: Folder '{class_folder}' not found. Skipping...")
            continue

        clean_files = list(class_folder.glob("*.wav"))
        out_class_folder = Path(output_dir) / class_name
        out_class_folder.mkdir(parents=True, exist_ok=True)

        print(
            f"\nProcessing '{class_name}' ({len(clean_files)} files found)..."
        )

        for clean_path in clean_files:
            # Load clean audio (mono=True converts to 1 channel, sr forces standard rate)
            clean_wav, sr = librosa.load(
                clean_path, sr=target_sr, mono=True
            )

            # Save clean file to the output directory
            sf.write(out_class_folder / clean_path.name, clean_wav, sr)

            # Generate augmented versions
            for i in range(num_augmented_per_file):
                # Pick a random silence clip
                noise_path = random.choice(silence_files)
                noise_wav, _ = librosa.load(
                    noise_path, sr=sr, mono=True
                )

                # Pick a random dB level (lower dB = noisier, higher dB = subtle background hum)
                random_snr = random.uniform(snr_range[0], snr_range[1])

                # Overlay noise
                noisy_wav = add_background_noise(
                    clean_wav, noise_wav, random_snr
                )

                # Save new augmented file
                aug_filename = f"{clean_path.stem}_noisy_{i+1}{clean_path.suffix}"
                sf.write(out_class_folder / aug_filename, noisy_wav, sr)

    print("\n✅ Augmentation Complete! Output saved to:", output_dir)


if __name__ == "__main__":
    # --- CONFIGURATION ---
    DATASET_DIR = r"D:\AI_Projects\threat_detection\audio\Datasets\True_Dataset\train"
    SILENCE_DIR = r"D:\AI_Projects\threat_detection\silence"
    OUTPUT_DIR = r"D:\AI_Projects\threat_detection\audio\augmented_dataset"

    # Classes to balance (e.g. Gun Shot: 300 -> 600, Car Horn: 360 -> 720)
    CLASSES_TO_AUGMENT = ["gun_shot", "car_horn"]

    augment_dataset(
        dataset_dir=DATASET_DIR,
        silence_dir=SILENCE_DIR,
        output_dir=OUTPUT_DIR,
        classes_to_augment=CLASSES_TO_AUGMENT,
        num_augmented_per_file=1,  # 1 new noisy sample per clean clip
        snr_range=(5.0, 20.0),  # Random SNR between 5 dB and 20 dB
        target_sr=44100,  # Matches your target sample rate
    )