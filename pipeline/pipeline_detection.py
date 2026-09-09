from threat_detection.tracking.tracker import Tracker
from threat_detection.face.recognizer import FaceRecognizer
from threat_detection.face.orientation import FaceOrientation
from threat_detection.face.mask_detector import MaskDetector
from threat_detection.tracking.movement_analyser import MovementAnalyzer
from threat_detection.tracking.loitering_detector import LoiteringDetector
from threat_detection.tracking.time_based_behaviour import TimeBehaviour
from threat_detection.weapons.detector import WeaponDetector
from threat_detection.threat.threat_engine import ThreatEngine

class DetectionPipeline:
    def __init__(self, process_every_n_frames=3):
        self.tracker = Tracker()
        self.recognizer = FaceRecognizer()
        self.face_orientation = FaceOrientation()
        self.mask = MaskDetector()
        self.movement_analyzer = MovementAnalyzer()
        self.loitering_detector = LoiteringDetector()
        self.time_behaviour = TimeBehaviour()
        self.weapon_detector = WeaponDetector()
        self.threat_engine = ThreatEngine()

        self.frame_count = 0
        self.process_every_n_frames = process_every_n_frames
        self.cached_people = {}

    def process(self, frame):
        self.frame_count += 1
        
        people = self.tracker.update(frame)

        run_heavy_analysis = (self.frame_count % self.process_every_n_frames == 0)

        if run_heavy_analysis:
            self.recognizer.update(frame, people)
            self.weapon_detector.update(frame, people)

            for person in people.values():
                self.mask.update(frame, person)
                self.face_orientation.update(person)

        for person in people.values():
            self.movement_analyzer.update(person)
            self.loitering_detector.update(person)
            self.time_behaviour.update(person)

        self.threat_engine.update_scene(people)

        self.cached_people = people
        return people
