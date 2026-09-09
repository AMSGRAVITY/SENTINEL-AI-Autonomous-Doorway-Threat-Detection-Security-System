from types import SimpleNamespace
from threat_detection.ui.event_logger import EventLogger


def create_person(
    track_id=1,
    identity="Unknown",
    movement="Standing",
    direction="Front",
    threat_level="LOW",
    threat_score=10,
):

    return SimpleNamespace(
        track_id=track_id,
        identity=identity,
        movement_state=movement,
        face_direction=direction,
        threat_level=threat_level,
        threat_score=threat_score,
    )


def main():

    logger = EventLogger()

    person = create_person()

    print("\n===== Event Logger Test =====\n")

    # Person enters
    logger.person_entered(person)

    # Identity detected
    logger.identity_changed(person)

    # Movement changes
    person.movement_state = "Walking"
    logger.movement_changed(person)

    person.movement_state = "Running"
    logger.movement_changed(person)

    # Face direction changes
    person.face_direction = "Left"
    logger.direction_changed(person)

    person.face_direction = "Right"
    logger.direction_changed(person)

    # Threat increases
    person.threat_level = "MEDIUM"
    person.threat_score = 42
    logger.threat_changed(person)

    person.threat_level = "HIGH"
    person.threat_score = 76
    logger.threat_changed(person)

    # Recording starts
    logger.recording_started(person)

    # Duplicate event (should NOT print)
    logger.recording_started(person)

    # Recording saved
    logger.recording_saved(
        person,
        "recording_20260610_143015.mp4"
    )

    # Alert
    logger.alert_sent(person)

    # Person leaves
    logger.person_left(person)
    

    print("\n===== Recent Events =====\n")

    for event in logger.get_recent_events():
        print(event)


if __name__ == "__main__":
    main()