from threat_detection.threat.threat_engine import ThreatEngine
from threat_detection.alert.email_template import EmailTemplate
from threat_detection.alert.email_sender import EmailSender
from threat_detection.core.person_track import PersonTrack

engine = ThreatEngine()
template = EmailTemplate()
person = PersonTrack(1)
mess = EmailSender()

snapshot_path = r"D:\AI_Projects\threat_detection\Saved\snapshot.png"
video_path = r"D:\AI_Projects\threat_detection\Saved\video.mp4"

person.identity = "Unknown"
person.movement_score = 15
person.loitering_score = 25
person.time_score = 20
person.face_orientation_score = 15
person.direction_changes = 13

engine.update(person)

subject = template.subject()
body = template.body(person)

print(subject)
print(body)

mess.send(subject, body, snapshot_path, video_path)