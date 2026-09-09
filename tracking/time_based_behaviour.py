from datetime import datetime
from threat_detection.config import (
    NIGHT_END,
    NIGHT_START,
    TIME_LOITER_NIGHT_SCORE,
    TIME_MASKED_NIGHT_SCORE,
    TIME_UNKNOWN_NIGHT_SCORE
)
from threat_detection.core.person_track import PersonTrack

class TimeBehaviour:
    def update(self, person: PersonTrack, current_time=None):
        score = 0
        
        if current_time is None:
            current_time = datetime.now()
        
        hour = current_time.hour
        night = (hour >= NIGHT_START or hour < NIGHT_END)

        if not night:
            person.time_score = 0
            return person
        
        if getattr(person, "identity", "Unknown") == "Unknown":
            score += TIME_UNKNOWN_NIGHT_SCORE
        
        if getattr(person, "is_loitering", False):
            score += TIME_LOITER_NIGHT_SCORE
        
        if getattr(person, "masked", False):
            score += TIME_MASKED_NIGHT_SCORE
        
        person.time_score = score
        return person