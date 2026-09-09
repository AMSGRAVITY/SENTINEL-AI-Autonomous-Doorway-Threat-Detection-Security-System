import cv2
import numpy as np
from threat_detection.ui.drawing import Drawing
from threat_detection.ui.dashboard import Dashboard
from threat_detection.ui.initialization import InitializeSystem
from threat_detection.ui.colors import (
    BG_DARK, CARD_BG, CARD_BORDER, CARD_HEADER, HUD_CYAN, WHITE, GRAY, CYAN, ALERT_CRIMSON, SAFE_COLOR, EMERALD_GREEN, FONT, SMALL_FONT, NORMAL_FONT, THICKNESS, TEXT_MUTED, TEXT_LIGHT
)

console = InitializeSystem()
console.check_hardware_status()
console.run_initialization_sequence()

class UIManager:
    def __init__(self, canvas_width=1920, canvas_height=1080):
        self.drawing = Drawing()
        self.dashboard = Dashboard()
        self.canvas_w = canvas_width
        self.canvas_h = canvas_height

    def render(self, frame, people: dict, recorder, fps, event_logger=None):
        """Renders 1920x1080 Command Center Dashboard with grid cards, video feed, donut chart, and alert stream."""
        canvas = np.zeros((self.canvas_h, self.canvas_w, 3), dtype=np.uint8)
        canvas[:] = BG_DARK
        has_member = any(person.identity != "Unknown" for person in people.values())

        # Background grid pattern
        for gx in range(0, self.canvas_w, 120):
            cv2.line(canvas, (gx, 0), (gx, self.canvas_h), (22, 17, 14), 1)
        for gy in range(0, self.canvas_h, 120):
            cv2.line(canvas, (0, gy), (self.canvas_w, gy), (22, 17, 14), 1)

        highest_person = self.dashboard.get_highest_threat_person(people)

        # 1. Top Navigation Bar
        self.dashboard.draw_top_header(canvas)

        # 2. Top Summary Metric Cards Row (5 Cards)
        self.dashboard.draw_top_summary_cards(canvas, people, recorder, highest_person, has_member)

        # 3. Main Center Row
        # --- Container 1: Live Video Monitoring Container ---
        vid_x, vid_y, vid_w, vid_h = 24, 155, 980, 620
        self.dashboard.draw_card_base(canvas, vid_x, vid_y, vid_w, vid_h, title="Live Video Monitoring  //  DoorCam - Main Entrance", icon_color=HUD_CYAN)

        # Draw overlays on camera stream before embedding
        self.drawing.draw_people(frame, people)
        self.drawing.draw_recording_indicator(frame, getattr(recorder, "recording", False))

        # Fit video inside container
        cam_w, cam_h = 940, 515
        cam_x, cam_y = vid_x + 20, vid_y + 48

        h, w = frame.shape[:2]
        if (w, h) != (cam_w, cam_h):
            frame_resized = cv2.resize(frame, (cam_w, cam_h))
        else:
            frame_resized = frame

        canvas[cam_y : cam_y + cam_h, cam_x : cam_x + cam_w] = frame_resized
        cv2.rectangle(canvas, (cam_x - 1, cam_y - 1), (cam_x + cam_w + 1, cam_y + cam_h + 1), CARD_BORDER, 1)

        # Video bottom controls overlay bar
        ctrl_y = vid_y + vid_h - 45
        cv2.rectangle(canvas, (cam_x, ctrl_y), (cam_x + cam_w, ctrl_y + 35), (28, 22, 18), -1)
        cv2.rectangle(canvas, (cam_x, ctrl_y), (cam_x + cam_w, ctrl_y + 35), CARD_BORDER, 1)
        
        cv2.putText(canvas, "● LIVE 480P", (cam_x + 15, ctrl_y + 22), FONT, 0.38, EMERALD_GREEN if not getattr(recorder, "recording", False) else ALERT_CRIMSON, 1, cv2.LINE_AA)
        cv2.putText(canvas, f"FPS: {fps:.1f}", (cam_x + 140, ctrl_y + 22), FONT, 0.38, CYAN, 1, cv2.LINE_AA)
        cv2.putText(canvas, "AI LOCK ACTIVE", (cam_x + cam_w - 140, ctrl_y + 22), FONT, 0.38, HUD_CYAN, 1, cv2.LINE_AA)

        # --- Container 2: Threat Reasons Overview Donut Card ---
        donut_x, donut_y, donut_w, donut_h = 1022, 155, 500, 620
        self.dashboard.draw_threat_reasons_donut(canvas, donut_x, donut_y, donut_w, donut_h, highest_person, has_member)

        # --- Container 3: Recent Alerts Log Card ---
        alerts_x, alerts_y, alerts_w, alerts_h = 1540, 155, 356, 620
        self.dashboard.draw_recent_alerts(canvas, alerts_x, alerts_y, alerts_w, alerts_h, event_logger)

        # 4. Bottom Metric Cards Row (5 Cards)
        bot_y = 790
        self.dashboard.draw_bottom_cards(canvas, bot_y, people, recorder, highest_person, event_logger)

        return canvas
