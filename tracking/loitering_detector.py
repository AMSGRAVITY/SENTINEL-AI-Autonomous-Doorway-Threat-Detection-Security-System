from threat_detection.config import (
    LOITER_AREA_THRESH,
    LOITER_SMALL_AREA,
    LOITER_MIN_VIS_TIME,
    LOITER_STAY_SCORE_30,
    LOITER_STAY_SCORE_60,
    LOITER_STAY_SCORE_90,
)
from threat_detection.core.person_track import PersonTrack

class LoiteringDetector:
    def __init__(
        self,
        min_vis_time=LOITER_MIN_VIS_TIME,
        area_thresh=LOITER_AREA_THRESH,
    ):
        self.min_vis_time = min_vis_time    
        self.area_thresh = area_thresh
    
    def update(self, person: PersonTrack):
        vis_time = getattr(person, "visible_time", 0.0)

        # Do not score loitering for new IDs visible for less than min_vis_time (30s)
        if vis_time < self.min_vis_time:
            person.loitering_score = 0
            person.is_loitering = False
            return person

        score = 0

        # 1. Stay Duration Points (5 pts @ 30s, 10 pts @ 60s, 15 pts @ 90s)
        if vis_time >= 90:
            score += LOITER_STAY_SCORE_90
        elif vis_time >= 60:
            score += LOITER_STAY_SCORE_60
        elif vis_time >= 30:
            score += LOITER_STAY_SCORE_30

        # 2. Small Area Stay Bonus (+20 pts if remaining within door area)
        is_small_area = False
        history = getattr(person, "center_history", [])
        if len(history) >= 2:
            xs = []
            ys = []
            for item in history:
                if isinstance(item, (tuple, list)):
                    pt = item[0] if isinstance(item[0], (tuple, list)) else item
                    xs.append(pt[0])
                    ys.append(pt[1])
            
            if xs and ys:
                w = max(xs) - min(xs)
                h = max(ys) - min(ys)
                if w < self.area_thresh and h < self.area_thresh:
                    is_small_area = True
                    score += LOITER_SMALL_AREA

        # Loitering status flags
        person.loitering_score = max(0, min(35, score))
        person.is_loitering = (vis_time >= self.min_vis_time and is_small_area)

        return person



        