import cv2
from threat_detection.core.person_track import PersonTrack

# COMMAND CENTER PALETTE (BGR)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Sci-Fi Neon Highlights
CYAN = (255, 240, 0)         # #00F0FF -> BGR: (255, 240, 0)
NEON_BLUE = (255, 160, 30)
NEON_AMBER = (0, 180, 255)
ALERT_CRIMSON = (60, 0, 255)
EMERALD_GREEN = (100, 240, 0)

GREEN = (0, 255, 120)
RED = (40, 40, 255)
YELLOW = (0, 230, 255)
ORANGE = (0, 140, 255)
BLUE = (255, 140, 0)

GRAY = (160, 160, 160)
DARK_GRAY = (65, 55, 45)

# Command Center Cards & Containers
BG_DARK = (16, 12, 10)          # Canvas background
CARD_BG = (26, 20, 16)          # Card container fill
CARD_HEADER = (36, 28, 22)      # Card title strip
CARD_BORDER = (60, 48, 38)      # Card outer border line
HUD_CYAN = (255, 220, 0)

TEXT_LIGHT = (245, 245, 245)
TEXT_MUTED = (160, 150, 140)

# THREAT COLORS
SAFE_COLOR = (120, 240, 0)      # Neon Emerald
LOW_COLOR = (0, 220, 255)       # Cyber Gold / Amber
MEDIUM_COLOR = (0, 140, 255)    # Orange
HIGH_COLOR = (40, 40, 255)      # Red
CRITICAL_COLOR = (255, 0, 220)  # Bright Neon Magenta / Purple

# FACE COLORS
KNOWN_COLOR = EMERALD_GREEN
UNKNOWN_COLOR = NEON_AMBER
NO_FACE_COLOR = GRAY
MASKED_COLOR = ALERT_CRIMSON

# RECORDING
RECORDING_ACTIVE = (40, 40, 255)   # Red
RECORDING_STANDBY = (100, 240, 0)  # Green

# PIE / DONUT CHART SLICE COLORS (BGR)
PIE_COLORS = [
    (255, 200, 0),   # Cyan
    (0, 180, 255),   # Amber
    (255, 0, 180),   # Purple/Pink
    (0, 230, 120),   # Mint
    (50, 100, 255),  # Crimson Red
    (255, 120, 50),  # Electric Blue
]

# FONT
FONT = cv2.FONT_HERSHEY_SIMPLEX

SMALL_FONT = 0.45
NORMAL_FONT = 0.60
LARGE_FONT = 0.80
TITLE_FONT = 1.0

THICKNESS = 2

# DASHBOARD
PANEL_WIDTH = 550
PADDING = 20
LINE_HEIGHT = 28

def get_person_color(person: PersonTrack):
    if not person:
        return UNKNOWN_COLOR
    if getattr(person, "masked", False):
        return MASKED_COLOR
    if not getattr(person, "has_face", True):
        return NO_FACE_COLOR
    if getattr(person, "identity", "Unknown") == "Unknown":
        return UNKNOWN_COLOR
    return KNOWN_COLOR

def get_threat_color(level):
    if not level:
        return SAFE_COLOR
    level = str(level).upper()

    if level == "SAFE":
        return SAFE_COLOR
    elif level == "LOW":
        return LOW_COLOR
    elif level == "MEDIUM":
        return MEDIUM_COLOR
    elif level == "HIGH":
        return HIGH_COLOR
    elif level == "CRITICAL":
        return CRITICAL_COLOR

    return WHITE

def get_threat_text(person: PersonTrack):
    return f"{person.threat_level} : ({person.threat_score})"
