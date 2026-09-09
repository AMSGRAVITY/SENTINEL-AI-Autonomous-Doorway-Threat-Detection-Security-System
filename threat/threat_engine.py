from threat_detection.config import (
    THREAT_LOW,
    THREAT_MEDIUM,
    THREAT_HIGH,
    THREAT_CRITICAL,
    THREAT_FACE_MASKED,
    THREAT_FACE_UNKNOWN,
    THREAT_FACE_NO_FACE,
    THREAT_KNOWN_MEMBER_MAX,
    CROWD_DENSITY_THRESHOLD_MED,
    CROWD_DENSITY_SCORE_MED,
    CROWD_DENSITY_THRESHOLD_HIGH,
    CROWD_DENSITY_SCORE_HIGH,
    THREAT_WEAPON_DETECTED,
)
from threat_detection.core.person_track import PersonTrack

class ThreatEngine:
    def __init__(
        self,
        low=THREAT_LOW,
        medium=THREAT_MEDIUM,
        high=THREAT_HIGH,
        critical=THREAT_CRITICAL
    ):
        self.low = low
        self.medium = medium
        self.high = high
        self.critical = critical

    def movement(self, person: PersonTrack):
        return person.movement_score

    def loitering(self, person: PersonTrack):
        return person.loitering_score

    def time(self, person: PersonTrack):
        return person.time_score

    def face(self, person: PersonTrack):
        score = person.face_orientation_score

        if not person.has_face:
            score += THREAT_FACE_NO_FACE
        else:
            if person.identity == "Unknown":
                score += THREAT_FACE_UNKNOWN

            if person.masked:
                score += THREAT_FACE_MASKED

        return score

    def calculate_crowd_density(self, total_people_count: int) -> int:
        if total_people_count >= CROWD_DENSITY_THRESHOLD_HIGH:
            return CROWD_DENSITY_SCORE_HIGH
        elif total_people_count >= CROWD_DENSITY_THRESHOLD_MED:
            return CROWD_DENSITY_SCORE_MED
        return 0

    def calculate_score(self, person: PersonTrack, total_people_count: int = 1, has_household_member: bool = False):
        density_score = self.calculate_crowd_density(total_people_count)
        weapon_score = THREAT_WEAPON_DETECTED if getattr(person, "weapon_detected", False) else 0

        person.score_breakdown = {
            "movement": self.movement(person),
            "face": self.face(person),
            "loitering": self.loitering(person),
            "crowd_density": density_score,
            "time": self.time(person),
            "weapon": weapon_score,
        }

        raw_score = sum(person.score_breakdown.values())

        # WEAPON SAFETY OVERRIDE:
        # Carrying a weapon overrides family whitelisting & escort caps!
        if getattr(person, "weapon_detected", False):
            person.threat_score = min(100, max(THREAT_CRITICAL, raw_score))
        elif person.identity != "Unknown" or has_household_member:
            person.threat_score = min(THREAT_KNOWN_MEMBER_MAX, raw_score)
        else:
            person.threat_score = min(100, max(0, raw_score))

        # Threat Reasons
        person.threat_reasons.clear()

        if getattr(person, "weapon_detected", False):
            w_names = ", ".join(getattr(person, "detected_weapons", ["weapon"]))
            person.threat_reasons.append(f"CRITICAL: Weapon Detected ({w_names})")

        if has_household_member and not getattr(person, "weapon_detected", False):
            person.threat_reasons.append("Family Escort Verified (SAFE)")

        if not person.has_face:
            person.threat_reasons.append("No Face Detected")

        if person.masked:
            person.threat_reasons.append("Masked Face")

        if person.identity == "Unknown" and not has_household_member and not getattr(person, "weapon_detected", False):
            person.threat_reasons.append("Unknown Face")

        if person.is_loitering:
            person.threat_reasons.append("Loitering")

        if getattr(person, "time_score", 0) > 0:
            person.threat_reasons.append("Night-Time Access")

        if person.direction_changes > 12:
            person.threat_reasons.append("Frequent Head Scanning")

        if total_people_count >= CROWD_DENSITY_THRESHOLD_HIGH:
            person.threat_reasons.append("High Crowd Density (5+)")
        elif total_people_count >= CROWD_DENSITY_THRESHOLD_MED:
            person.threat_reasons.append("Medium Crowd Density (3+)")



    def calculate_level(self, person: PersonTrack):
        score = person.threat_score

        if score >= self.critical:
            person.threat_level = "CRITICAL"
        elif score >= self.high:
            person.threat_level = "HIGH"
        elif score >= self.medium:
            person.threat_level = "MEDIUM"
        elif score >= self.low:
            person.threat_level = "LOW"
        else:
            person.threat_level = "SAFE"

    def decide_actions(self, person: PersonTrack):
        person.should_record = False
        person.should_alert = False

        if person.threat_level in ["HIGH", "CRITICAL"]:
            person.should_record = True

        if person.threat_level == "CRITICAL":
            person.should_alert = True

    def update_scene(self, people: dict):
        """Evaluates entire scene context (total people & household member presence)."""
        total_people = len(people)
        has_household_member = any(
            getattr(p, "identity", "Unknown") != "Unknown" for p in people.values()
        )

        for person in people.values():
            self.calculate_score(person, total_people, has_household_member)
            self.calculate_level(person)
            self.decide_actions(person)

        return people

    def update(self, person: PersonTrack):
        """Single-person update for backward compatibility."""
        has_member = getattr(person, "identity", "Unknown") != "Unknown"
        self.calculate_score(person, total_people_count=1, has_household_member=has_member)
        self.calculate_level(person)
        self.decide_actions(person)
        return person
