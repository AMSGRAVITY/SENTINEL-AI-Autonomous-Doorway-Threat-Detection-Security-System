from dataclasses import dataclass, field
from collections import deque
from typing import Tuple, Optional
import time

@dataclass
class PersonTrack:

    # Tracking:
    track_id: int
    bbox: Tuple[int, int, int, int] = (0, 0, 0, 0)
    center: Tuple[int, int] = (0, 0)
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    visible_time: float = 0.0

    # Movement:
    speed: float = 0.0
    movement_state: str = "Standing"
    movement_score: int = 0
    standing_time: float = 0.0
    walking_time: float = 0.0
    running_time: float = 0.0

    # Zone:
    current_zone: str = "None"

    # Recording
    recording: bool = False

    # History
    center_history: deque = field(default_factory=lambda: deque(maxlen=20))

    # Loitering
    is_loitering: bool = False
    loitering_score: int = 0

    # Time-Based Behaviour
    time_score: int = 0

    # Mask-Detection
    masked: bool = False
    mask_confidence: float = 0.0

    # Face-Recognition
    has_face: bool = False
    identity: str = "Unknown"
    face_match_score: float = 0.0
    face_bbox: tuple | None = None
    face_landmarks: list | None = None
    face_embeddings: any = None
    face: any = None
    
    # Face-Orientation
    face_direction: str = "Unknown"
    last_face_direction: str = "Unknown"
    candidate_face_direction: str = "Unknown"
    candidate_direction_frames: int = 0
    direction_changes: int = 0
    face_direction_history: deque = field(default_factory=lambda: deque(maxlen=30))
    face_orientation_score: int = 0

    # Record
    should_record: bool = False
    should_alert: bool = False
    alert_sent: bool = False

    # Threat
    threat_score: int = 0
    threat_level: str = "Safe"

    # Weapon Detection
    weapon_detected: bool = False
    weapon_candidate_count: int = 0
    detected_weapons: list[str] = field(default_factory=list)
    weapon_boxes: list[tuple] = field(default_factory=list)
    weapon_confidence: float = 0.0


    # Display
    threat_reasons: list[str] = field(default_factory=list)
    score_breakdown: dict[str, int] = field(default_factory=dict)