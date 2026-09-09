import threading, time
from threat_detection.alert.email_sender import EmailSender
from threat_detection.alert.email_template import EmailTemplate
from threat_detection.core.person_track import PersonTrack

class AlertManager:
    def __init__(self, event_logger=None):
        self.email_sender = EmailSender()
        self.template = EmailTemplate()
        self.event_logger = event_logger

        self.session_active = False
        self.critical_triggered = False
        self.active_highest_person = None
        self.active_snapshot_path = None
        self.session_start_time = None

    def start_session(self):
        if not self.session_active:
            self.session_active = True
            self.session_start_time = time.time()

    def get_highest_person(self, people: dict) -> PersonTrack:
        if not people:
            return None

        return max(people.values(), key=lambda p: getattr(p, "threat_score", 0))

    def reset_session(self):
        self.session_active = False
        self.critical_triggered = False
        self.active_highest_person = None
        self.active_snapshot_path = None 
        self.session_start_time = None

    # STAGE 1:
    def send_immediate_alert_async(self, people: dict, snapshot_path: str):

        if not people:
            return None

        self.critical_triggered = True
        self.active_snapshot_path = snapshot_path
        self.active_highest_person = self.get_highest_person(people)

        def _worker():
            total_people = len(people)
            critical_count = sum(1 for p in people.values() if p.threat_level.upper() == "CRITICAL")

            w_detected = getattr(self.active_highest_person, "weapon_detected", False)
            w_list = getattr(self.active_highest_person, "detected_weapons", [])
            w_flag = f" [WEAPON: {', '.join(w_list).upper()}]" if (w_detected and w_list) else (" [WEAPON DETECTED]" if w_detected else "")

            subject = f"[CRITICAL THREAT]{w_flag} Target #{self.active_highest_person.track_id} ({self.active_highest_person.identity})"

            body = self.template.consolidated_body(self.active_highest_person, total_people, critical_count, "immediate")

            print("[ALERT MANAGER] Sending Stage 1 Immediate Alert in Background...")
            success = self.email_sender.send(subject, body, snapshot_path=snapshot_path, video_path=None)

            if success and self.event_logger:
                self.event_logger.alert_sent(self.active_highest_person, stage="Immediate")

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def send_video_followup_async(self, video_path: str):

        if not self.critical_triggered:
            print("[ALERT MANAGER] Recording Finished, but no Critical Threat was detected. No Mail will be sent")
            self.reset_session()
            return

        if not video_path:
            print("[ALERT MANAGER ERROR] Cannot Send Video Follow up: Videopath is None")
            self.reset_session()
            return

        duration = time.time() - self.session_start_time
        target_person = self.active_highest_person

        self.reset_session()

        def _worker():

            subject = f"[INCIDENT RESOLVED] Video Recording Attatched - Subject #{target_person.track_id}"
            body = self.template.consolidated_body(highest_person=target_person, stage="followup", duration_sec=duration)

            print("[ALERT MANAGER] Sending Stage 2 Follow-up Alert with the recorded Video in Background...")
            success = self.email_sender.send(subject, body, snapshot_path=None, video_path=video_path)

            if success and self.event_logger:
                self.event_logger.alert_sent(target_person, stage="Video Follow-up")

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()