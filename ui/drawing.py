import cv2, math, time
import numpy as np
from threat_detection.ui.colors import *
from threat_detection.core.person_track import PersonTrack

class Drawing:

    def __init__(self):
        pass

    # Basic Text Drawing
    def draw_text(
        self,
        frame,
        x,
        y,
        text,
        color=WHITE,
        font_scale=NORMAL_FONT,
        thickness=THICKNESS
    ):
        cv2.putText(
            frame,
            str(text),
            (int(x), int(y)),
            FONT,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA
        )

    # Sci-Fi Corner Bounding Box & Target Lock
    def draw_corner_bbox(self, frame, bbox, color, thickness=2, line_len=24):
        x1, y1, x2, y2 = map(int, bbox)
        w, h = x2 - x1, y2 - y1

        # Translucent bounding tint
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
        cv2.addWeighted(overlay, 0.08, frame, 0.92, 0, frame)

        # Draw outer thin frame border
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1, cv2.LINE_AA)

        # Draw heavy sci-fi corner brackets
        # Top Left
        cv2.line(frame, (x1, y1), (x1 + line_len, y1), color, thickness + 1)
        cv2.line(frame, (x1, y1), (x1, y1 + line_len), color, thickness + 1)
        cv2.circle(frame, (x1, y1), 3, color, -1)

        # Top Right
        cv2.line(frame, (x2, y1), (x2 - line_len, y1), color, thickness + 1)
        cv2.line(frame, (x2, y1), (x2, y1 + line_len), color, thickness + 1)
        cv2.circle(frame, (x2, y1), 3, color, -1)

        # Bottom Left
        cv2.line(frame, (x1, y2), (x1 + line_len, y2), color, thickness + 1)
        cv2.line(frame, (x1, y2), (x1, y2 - line_len), color, thickness + 1)
        cv2.circle(frame, (x1, y2), 3, color, -1)

        # Bottom Right
        cv2.line(frame, (x2, y2), (x2 - line_len, y2), color, thickness + 1)
        cv2.line(frame, (x2, y2), (x2, y2 - line_len), color, thickness + 1)
        cv2.circle(frame, (x2, y2), 3, color, -1)

        # Center Targeting Reticle (Crosshair)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        r = min(16, max(8, w // 8))
        cv2.circle(frame, (cx, cy), r, color, 1, cv2.LINE_AA)
        cv2.line(frame, (cx - r - 4, cy), (cx - r + 2, cy), color, 1)
        cv2.line(frame, (cx + r - 2, cy), (cx + r + 4, cy), color, 1)
        cv2.line(frame, (cx, cy - r - 4), (cx, cy - r + 2), color, 1)
        cv2.line(frame, (cx, cy + r - 2), (cx, cy + r + 4), color, 1)

    def draw_label(self, frame, x, y, text, color):
        (w, h), baseline = cv2.getTextSize(
            str(text),
            FONT,
            NORMAL_FONT,
            THICKNESS
        )

        # Semi-transparent dark pill background
        sub_img = frame[y - h - 10 : y + baseline + 4, x - 2 : x + w + 12]
        if sub_img.shape[0] > 0 and sub_img.shape[1] > 0:
            black_rect = np.full(sub_img.shape, (20, 16, 12), dtype=np.uint8)
            res = cv2.addWeighted(sub_img, 0.3, black_rect, 0.7, 0)
            frame[y - h - 10 : y + baseline + 4, x - 2 : x + w + 12] = res

        cv2.rectangle(frame, (x - 2, y - h - 10), (x + w + 12, y + baseline + 4), color, 1, cv2.LINE_AA)

        self.draw_text(
            frame,
            x + 4,
            y - 4,
            text,
            color,
            NORMAL_FONT,
            1
        )

    # Person Drawing
    def draw_person(self, frame, person: PersonTrack):
        x1, y1, x2, y2 = map(int, person.bbox)
        color = get_person_color(person)

        # Pulse effect for HIGH / CRITICAL threat targets
        t_level = str(person.threat_level).upper()
        if t_level == "CRITICAL":
            pulse = int((math.sin(time.time() * 12) + 1) * 127)
            color = (pulse, 0, 255)  # Pulsing bright purple/red
        elif t_level == "HIGH":
            pulse = int((math.sin(time.time() * 8) + 1) * 60)
            color = (0, 100 + pulse, 255)

        # Draw sci-fi corner bounding box
        self.draw_corner_bbox(frame, person.bbox, color, thickness=2, line_len=22)

        # Draw Trajectory Trace with glowing dots
        history = person.center_history
        if len(history) > 1:
            for i in range(1, len(history)):
                pt1 = (int(history[i-1][0][0]), int(history[i-1][0][1]))
                pt2 = (int(history[i][0][0]), int(history[i][0][1]))
                alpha = i / len(history)
                tail_color = tuple(int(c * alpha) for c in color)
                cv2.line(frame, pt1, pt2, tail_color, 2, cv2.LINE_AA)
                cv2.circle(frame, pt2, 2, tail_color, -1)

        # Sci-Fi Subject Telemetry Badge (Top Left of Bounding Box)
        labels = [
            f"TARGET #{person.track_id}",
            f"ID: {person.identity}",
            f"THREAT: {person.threat_level} [{person.threat_score}]"
        ]

        current_y = y1 - 10
        for text in reversed(labels):
            (w, h), baseline = cv2.getTextSize(str(text), FONT, SMALL_FONT, 1)
            
            # Badge background
            bx1, by1 = x1, current_y - h - 6
            bx2, by2 = x1 + w + 12, current_y + 4

            if bx1 >= 0 and by1 >= 0 and bx2 <= frame.shape[1] and by2 <= frame.shape[0]:
                sub_area = frame[by1:by2, bx1:bx2]
                dark_bg = np.full(sub_area.shape, (15, 10, 8), dtype=np.uint8)
                frame[by1:by2, bx1:bx2] = cv2.addWeighted(sub_area, 0.25, dark_bg, 0.75, 0)
                cv2.rectangle(frame, (bx1, by1), (bx2, by2), color, 1, cv2.LINE_AA)

            self.draw_text(frame, x1 + 6, current_y - 2, text, color, SMALL_FONT, 1)
            current_y -= (h + 10)

        # Draw Weapon Target Bounding Boxes & Reticle Tags
        if getattr(person, "weapon_detected", False) and getattr(person, "weapon_boxes", []):
            for wbox in person.weapon_boxes:
                wx1, wy1, wx2, wy2 = map(int, wbox)
                cv2.rectangle(frame, (wx1, wy1), (wx2, wy2), (0, 0, 255), 2, cv2.LINE_AA)
                cv2.rectangle(frame, (wx1 - 1, wy1 - 18), (wx2, wy1), (20, 10, 60), -1)
                cv2.rectangle(frame, (wx1 - 1, wy1 - 18), (wx2, wy1), (0, 0, 255), 1)
                w_label = f"⚠ WEAPON: {', '.join(person.detected_weapons).upper()}"
                cv2.putText(frame, w_label, (wx1 + 4, wy1 - 4), FONT, 0.38, (0, 0, 255), 1, cv2.LINE_AA)


    def draw_people(self, frame, people: dict):
        for person in people.values():
            self.draw_person(frame, person)

    # HUD Visuals
    def draw_fps(self, frame, fps):
        self.draw_text(
            frame,
            15,
            30,
            f"FPS : {fps:.1f}",
            CYAN,
            SMALL_FONT,
            1
        )

    def draw_recording_indicator(self, frame, recording, duration_sec=0.0):
        if not recording:
            return

        text = f"● REC [{int(duration_sec):02d}s]"

        (w, h), baseline = cv2.getTextSize(str(text), FONT, SMALL_FONT, 1)
        x = frame.shape[1] - w - 30
        y = 35

        # Flash red recording marker
        if int(time.time() * 3) % 2 == 0:
            cv2.circle(frame, (x - 12, y - 5), 6, (40, 40, 255), -1)

        cv2.rectangle(frame, (x - 8, y - h - 6), (x + w + 8, y + 6), (20, 15, 60), -1)
        cv2.rectangle(frame, (x - 8, y - h - 6), (x + w + 8, y + 6), ALERT_CRIMSON, 1)
        self.draw_text(frame, x, y, text, WHITE, SMALL_FONT, 1)