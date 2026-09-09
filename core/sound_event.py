from dataclasses import dataclass, field
import time

@dataclass
class SoundEvent:
    
    # Classification
    label: str = "Unknown"
    confidence: float = 0.0
    sound_score: int = 0

    # Timing
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0

    probability: dict = field(default_factory=dict)

    # Input-Sources
    source: str = "microphone"