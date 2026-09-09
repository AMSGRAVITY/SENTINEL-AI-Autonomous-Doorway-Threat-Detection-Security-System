from threat_detection.config import (
    YAW_THRESH,
    PITCH_THRESH,
    LOOK_LEFT_SCORE,
    LOOK_RIGHT_SCORE,
    LOOK_UP_SCORE,
    LOOK_DOWN_SCORE,
    SCAN_12_SCORE,
    SCAN_6_SCORE
)
from threat_detection.core.person_track import PersonTrack

class FaceOrientation:
    def __init__(self):
        pass

    def update(self, person: PersonTrack):
        
        if not person.has_face or person.face_landmarks is None:
            return person
        
        kps = person.face_landmarks

        left_eye = kps[0]
        right_eye = kps[1]
        nose = kps[2]
        left_mouth = kps[3]
        right_mouth = kps[4]

        # Calculating Yaw
        # Yaw is nothing but z-axis rotation of our head i.e looking left or right

        eye_center_x = (left_eye[0] + right_eye[0]) / 2
        eye_dist = abs(right_eye[0] - left_eye[0])

        if eye_dist < 1:
            eye_dist = 1
        
        yaw_ratio = (nose[0] - eye_center_x) / eye_dist

        # Calculating Pitch
        # Pitch is x-axis rotation of our head i.e looking up or down

        eye_center_y = (left_eye[1] + right_eye[1]) / 2
        mouth_center_y = (left_mouth[1] + right_mouth[1]) / 2
        face_height = abs(eye_center_y - mouth_center_y)

        if face_height < 1:
            face_height = 1
        
        pitch_ratio = (nose[1] - eye_center_y) / face_height

        dir = "Straight"

        # Direction


        if yaw_ratio < -YAW_THRESH:
            dir = "Left"
        elif yaw_ratio > YAW_THRESH:
            dir = "Right"
        
        elif pitch_ratio < 0.4 - PITCH_THRESH:
            dir = "Up"
        elif pitch_ratio > 0.4 + PITCH_THRESH:
            dir = "Down"

        
        
        # Direction History

        if dir != person.candidate_face_direction:
            person.candidate_face_direction = dir
            person.candidate_direction_frames = 1
        else:
            person.candidate_direction_frames += 1
        
        if person.candidate_direction_frames >= 3:
            if person.face_direction != person.candidate_face_direction:
                if person.face_direction != "Unknown":
                    person.direction_changes += 1
                person.face_direction = person.candidate_face_direction
                person.face_direction_history.append(person.face_direction)

        # Orientation Score

        score = 0

        if person.face_direction == "Left":
            score += LOOK_LEFT_SCORE
        elif person.face_direction == "Right":
            score += LOOK_RIGHT_SCORE
        elif person.face_direction == "Up":
            score += LOOK_UP_SCORE
        elif person.face_direction == "Down":
            score += LOOK_DOWN_SCORE
        
        if person.direction_changes > 12:
            score += SCAN_12_SCORE
        elif person.direction_changes > 6:
            score += SCAN_6_SCORE
        
        person.face_orientation_score = score

        return person