import math
from threat_detection.config import (
    MODERATE_SPEED,
    FAST_SPEED,
    HISTORY_LENGTH,
    MOVEMENT_STILL,
    MOVEMENT_MODERATE,
    MOVEMENT_FAST
)
from threat_detection.core.person_track import PersonTrack

class MovementAnalyzer:
    def __init__(
            self,
            moderate_thresh = MODERATE_SPEED,
            fast_thresh = FAST_SPEED,
            history_length = HISTORY_LENGTH
    ):
        self.moderate_thresh = moderate_thresh
        self.fast_thresh = fast_thresh
        self.history_length = history_length
    
    def update(self, person: PersonTrack):
        score = 0

        if len(person.center_history) < 2:
            return person
        
        current_center, current_time = person.center_history[-1]
        prev_center, prev_time = person.center_history[-2]

        dx = current_center[0] - prev_center[0]
        dy = current_center[1] - prev_center[1]

        distance = math.sqrt(dx*dx + dy*dy)
        dt = current_time - prev_time

        if dt == 0:
            dt = 1e-6
        
        speed = distance/dt
        person.speed = speed

        if speed < self.moderate_thresh:
            movement = "No Movement"
            person.standing_time += dt
            score += MOVEMENT_STILL

        elif speed < self.fast_thresh:
            movement = "Moderate"
            person.walking_time += dt
            score += MOVEMENT_MODERATE

        else:
            movement = "Fast"
            person.running_time += dt
            score += MOVEMENT_FAST
        
        person.movement_state = movement
        person.speed = speed
        person.movement_score = score

        return person