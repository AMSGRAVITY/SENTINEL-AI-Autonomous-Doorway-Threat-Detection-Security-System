from dataclasses import dataclass
from datetime import datetime


@dataclass
class VideoClip:

    # Recording

    filename: str
    start_time: datetime
    end_time: datetime | None = None
    duration: float = 0.0
    saved: bool = False

    # Cause

    trigger_person: int | None = None
    trigger_reason: str = ""
    threat_score: int = 0