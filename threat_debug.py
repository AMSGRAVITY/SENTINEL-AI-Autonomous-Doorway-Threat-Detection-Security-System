from threat_detection.core.person_track import PersonTrack
from threat_detection.threat.threat_engine import ThreatEngine

engine = ThreatEngine()

# CASE 1: Recognized Household Member (Score < 10)
p1 = PersonTrack(track_id=1, identity="Maneesh", has_face=True, movement_score=20, loitering_score=30)
engine.update(p1)

print("--- CASE 1: Recognized Household Member ---")
print(f"Score: {p1.threat_score} | Level: {p1.threat_level} | Record: {p1.should_record}")
print(f"Reasons: {p1.threat_reasons}")
print(f"Breakdown: {p1.score_breakdown}\n")

# CASE 2: YOLO Person Detected with No Face (+20 Penalty)
p2 = PersonTrack(track_id=2, identity="Unknown", has_face=False, loitering_score=15)
engine.update(p2)

print("--- CASE 2: Person Detected with No Face (+20 Penalty) ---")
print(f"Score: {p2.threat_score} | Level: {p2.threat_level} | Record: {p2.should_record}")
print(f"Reasons: {p2.threat_reasons}")
print(f"Breakdown: {p2.score_breakdown}\n")

# CASE 3: Group of 5 Unknown People (High Crowd Density Penalty +30)
group_unknown = {
    i: PersonTrack(track_id=i, identity="Unknown", has_face=True, loitering_score=20) for i in range(1, 6)
}
engine.update_scene(group_unknown)

print("--- CASE 3: Group of 5 Unknown People (Crowd Density +30) ---")
print(f"Target #1 Score: {group_unknown[1].threat_score} | Level: {group_unknown[1].threat_level}")
print(f"Reasons: {group_unknown[1].threat_reasons}")
print(f"Breakdown: {group_unknown[1].score_breakdown}\n")

# CASE 4: Group of 5 People with 1 Recognized Household Member (Family Escort Override < 10)
group_family = {
    1: PersonTrack(track_id=1, identity="Maneesh", has_face=True, loitering_score=30),
    2: PersonTrack(track_id=2, identity="Unknown", has_face=True, loitering_score=30),
    3: PersonTrack(track_id=3, identity="Unknown", has_face=False, loitering_score=30),
    4: PersonTrack(track_id=4, identity="Unknown", has_face=True, loitering_score=30),
    5: PersonTrack(track_id=5, identity="Unknown", has_face=True, loitering_score=30),
}
engine.update_scene(group_family)

print("--- CASE 4: Group with 1 Recognized Household Member (Escort Override < 10) ---")
print(f"Household Member #1 Score: {group_family[1].threat_score} | Level: {group_family[1].threat_level}")
print(f"Accompanying Guest #2 Score: {group_family[2].threat_score} | Level: {group_family[2].threat_level}")
print(f"Reasons: {group_family[2].threat_reasons}")
print(f"Breakdown: {group_family[2].score_breakdown}\n")