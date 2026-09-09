from collections import deque
from datetime import datetime
from threat_detection.core.person_track import PersonTrack

# ANSI Color Codes for Terminal Styling
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Palette
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
WHITE = "\033[97m"

# Mapping Event Types to Styled Color Badges
EVENT_BADGES = {
    "ENTER": f"{GREEN}{BOLD} ENTER {RESET}",
    "EXIT": f"{MAGENTA}{BOLD}  EXIT {RESET}",
    "IDENTITY": f"{CYAN}{BOLD} ID    {RESET}",
    "MOVEMENT": f"{BLUE}{BOLD} MOVE  {RESET}",
    "DIRECTION": f"{WHITE}{BOLD} LOOK  {RESET}",
    "THREAT": f"{RED}{BOLD} THREAT{RESET}",
    "RECORDING": f"{YELLOW}{BOLD} REC   {RESET}",
    "RECORDING_STOP": f"{YELLOW}{DIM} REC   {RESET}",
    "SAVE": f"{GREEN} SAVE  {RESET}",
    "ALERT": f"{RED}{BOLD} ALERT {RESET}",
}


class EventLogger:

    def __init__(self, max_events=100):
        self.events = deque(maxlen=max_events)
        self.previous_people = set()
        self.person_states = {}
        # Prevents printing the same event every frame
        self.last_events = {}
        self.alert_count = 0


    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def _create_event(self, person_id, event_type, message):
        return {
            "time": self._timestamp(),
            "person_id": person_id,
            "type": event_type,
            "message": message,
        }

    def _colorize_message(self, message: str) -> str:
        """Dynamically applies colors inside threat and status messages."""
        if "CRITICAL" in message or "HIGH" in message:
            return f"{RED}{BOLD}{message}{RESET}"
        elif "MEDIUM" in message:
            return f"{YELLOW}{BOLD}{message}{RESET}"
        elif "SAFE" in message or "LOW" in message:
            return f"{GREEN}{message}{RESET}"
        return message

    def _store(self, event):
        self.events.append(event)

        # Get badge style or fallback to default
        event_type = event["type"]
        badge = EVENT_BADGES.get(event_type, f" {event_type:<6} ")
        
        # Colorize threat scores / state messages
        styled_msg = self._colorize_message(event["message"])

        # Clean formatted output line
        print(
            f"{DIM}[{event['time']}]{RESET} "
            f"[{badge}] "
            f"{BOLD}ID:{event['person_id']:<3}{RESET} ➔ "
            f"{styled_msg}"
        )

    # Public
    def log(self, person_id, event_type, message):
        key = (person_id, event_type)

        if self.last_events.get(key) == message:
            return

        self.last_events[key] = message
        event = self._create_event(person_id, event_type, message)
        self._store(event)

    # Convenience Methods
    def person_entered(self, person: PersonTrack):
        level = str(getattr(person, "threat_level", "SAFE")).upper()
        if level in ["HIGH", "CRITICAL"]:
            self.alert_count += 1
        self.log(person.track_id, "ENTER", "Person entered scene.")

    def person_left(self, track_id: int):
        self.log(track_id, "EXIT", "Person left scene.")

    def identity_changed(self, person: PersonTrack):
        self.log(person.track_id, "IDENTITY", f"Identity: {person.identity}")

    def movement_changed(self, person: PersonTrack):
        self.log(person.track_id, "MOVEMENT", f"Movement: {person.movement_state}")

    def direction_changed(self, person: PersonTrack):
        self.log(person.track_id, "DIRECTION", f"Looking: {person.face_direction}")

    def threat_changed(self, person: PersonTrack):
        level = str(getattr(person, "threat_level", "SAFE")).upper()
        if level in ["HIGH", "CRITICAL"]:
            self.alert_count += 1

        self.log(
            person.track_id,
            "THREAT",
            f"Threat -> {person.threat_level} ({person.threat_score})"
        )

    def recording_started(self, person: PersonTrack):
        self.log(person.track_id, "RECORDING", "Recording started.")

    def recording_stopped(self, person: PersonTrack):
        self.log(person.track_id, "RECORDING_STOP", "Recording stopped.")

    def recording_saved(self, person: PersonTrack, filename):
        self.log(person.track_id, "SAVE", f"Recording saved: {filename}")

    def alert_sent(self, person: PersonTrack, stage: str):
        self.alert_count += 1
        self.log(person.track_id, "ALERT", f"{stage} Alert Sent")


    # Access
    def get_recent_events(self, count=10):
        return list(self.events)[-count:]

    def clear(self):
        self.events.clear()
        self.last_events.clear()

    # Update
    def update(self, people):
        current_people = set(people.keys())

        # Person Entered
        for track_id in current_people - self.previous_people:
            person = people[track_id]
            self.person_entered(person)
            self.person_states[track_id] = {
                "identity": person.identity,
                "movement": person.movement_state,
                "direction": person.face_direction,
                "threat": (person.threat_level, person.threat_score),
            }

        # Person Left
        for track_id in self.previous_people - current_people:
            state = self.person_states.pop(track_id, None)
            self.person_left(track_id)

        # State Changes
        for person in people.values():
            state = self.person_states.setdefault(person.track_id, {})

            if state.get("identity") != person.identity:
                self.identity_changed(person)
                state["identity"] = person.identity

            if state.get("movement") != person.movement_state:
                self.movement_changed(person)
                state["movement"] = person.movement_state

            if state.get("direction") != person.face_direction:
                self.direction_changed(person)
                state["direction"] = person.face_direction

            threat = (person.threat_level, person.threat_score)

            if state.get("threat") != threat:
                self.threat_changed(person)
                state["threat"] = threat

        self.previous_people = current_people