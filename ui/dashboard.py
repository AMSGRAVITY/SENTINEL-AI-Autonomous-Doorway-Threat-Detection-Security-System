import cv2, math, time
from datetime import datetime
import numpy as np
from threat_detection.ui.colors import *
from threat_detection.core.person_track import PersonTrack

class Dashboard:
    def __init__(self):
        pass

    def draw_warning_icon(self, frame, center, size=20, color=(0, 255, 255)):
        """Draws a warning triangle with an exclamation mark.

        center: (x, y) tuple for the center of the icon
        size: height/width scale in pixels
        color: BGR tuple (default: Yellow -> (0, 255, 255))
        """
        cx, cy = center
        half = size // 2

        # 1. Triangle vertices
        pts = np.array(
            [[cx, cy - half], [cx - half, cy + half], [cx + half, cy + half]],
            np.int32,
        )
        cv2.fillPoly(frame, [pts], color)

        # 2. Exclamation mark inside (Black for contrast)
        # Top line of '!'
        cv2.line(
            frame,
            (cx, cy - half + 5),
            (cx, cy + 2),
            (0, 0, 0),
            2,
            lineType=cv2.LINE_AA,
        )
        # Dot of '!'
        cv2.circle(frame, (cx, cy + half - 4), 1, (0, 0, 0), -1, lineType=cv2.LINE_AA)


    def draw_check_icon(self, frame, center, size=20, color=(0, 255, 0)):
        """Draws a green checkmark/tick.

        center: (x, y) tuple
        size: bounding box scale
        color: BGR tuple (default: Green -> (0, 255, 0))
        """
        cx, cy = center
        half = size // 2

        # Define the 3 control points of the checkmark line
        p1 = (cx - half, cy)
        p2 = (cx - half // 3, cy + half // 2)
        p3 = (cx + half, cy - half // 2)

        pts = np.array([p1, p2, p3], np.int32)
        cv2.polylines(
            frame, [pts], isClosed=False, color=color, thickness=2, lineType=cv2.LINE_AA
        )

    # Core Card Base Helper
    def draw_card_base(self, frame, x, y, w, h, title=None, icon_color=HUD_CYAN):
        x, y, w, h = int(x), int(y), int(w), int(h)
        sub_img = frame[y:y+h, x:x+w]
        if sub_img.shape[0] > 0 and sub_img.shape[1] > 0:
            dark_panel = np.full(sub_img.shape, CARD_BG, dtype=np.uint8)
            frame[y:y+h, x:x+w] = cv2.addWeighted(sub_img, 0.15, dark_panel, 0.85, 0)
            
            # Card Outer Border
            cv2.rectangle(frame, (x, y), (x + w, y + h), CARD_BORDER, 1, cv2.LINE_AA)
            cv2.rectangle(frame, (x - 1, y - 1), (x + w + 1, y + h + 1), (20, 16, 12), 1, cv2.LINE_AA)

        if title:
            # Title header strip
            cv2.rectangle(frame, (x + 1, y + 1), (x + w - 1, y + 36), CARD_HEADER, -1)
            cv2.line(frame, (x, y + 36), (x + w, y + 36), CARD_BORDER, 1)

            # Left accent pill
            cv2.rectangle(frame, (x + 12, y + 10), (x + 16, y + 26), icon_color, -1)

            # Title Text
            cv2.putText(
                frame,
                str(title),
                (x + 24, y + 24),
                FONT,
                SMALL_FONT,
                TEXT_LIGHT,
                1,
                cv2.LINE_AA
            )

    # Top Header Bar (System Name, Timestamp, Controls)
    def draw_top_header(self, frame):
        h, w = frame.shape[:2]
        hdr_h = 45

        # Background bar
        cv2.rectangle(frame, (0, 0), (w, hdr_h), CARD_HEADER, -1)
        cv2.line(frame, (0, hdr_h), (w, hdr_h), CARD_BORDER, 1)

        # Brand / Logo
        cv2.rectangle(frame, (20, 10), (40, 30), HUD_CYAN, -1)
        cv2.putText(frame, "K", (26, 26), FONT, 0.6, BLACK, 2, cv2.LINE_AA)
        
        cv2.putText(frame, "SENTINEL-AI", (50, 28), FONT, 0.75, WHITE, 2, cv2.LINE_AA)
        cv2.putText(frame, "|  DoorCam AI Video Analytics Command Center", (200, 26), FONT, 0.45, TEXT_MUTED, 1, cv2.LINE_AA)

        # Live Timestamp
        time_str = datetime.now().strftime("%b %d, %Y  %H:%M:%S")
        cv2.putText(frame, time_str, (w - 320, 26), FONT, 0.45, CYAN, 1, cv2.LINE_AA)
        
        # Site selector badge
        cv2.rectangle(frame, (w - 140, 8), (w - 20, 34), (45, 35, 28), -1)
        cv2.rectangle(frame, (w - 140, 8), (w - 20, 34), CARD_BORDER, 1)
        cv2.putText(frame, "DoorCam - Site 01", (w - 132, 24), FONT, 0.38, TEXT_LIGHT, 1, cv2.LINE_AA)

    # Top Metric Summary Cards Row (5 Cards)
    def draw_top_summary_cards(self, frame, people, recorder, highest_person: PersonTrack, has_member: bool):
        card_y = 55
        card_h = 88
        card_w = 360
        gap = 18
        start_x = 24

        # Card 1: Mask Status (Red if Masked, Green if No Mask)
        is_masked = False
        if highest_person:
            is_masked = getattr(highest_person, "masked", False) or ("Face_Mask" in getattr(highest_person, "score_breakdown", {}))
        
        mask_title = "Mask Status"
        mask_val = "Detected" if is_masked else "No Mask Detected"
        if has_member:
            mask_sub = "Clear Facial View"
        else:
            mask_sub = "Face Mask Flagged" if is_masked else "Clear Facial View"
        mask_color = ALERT_CRIMSON if is_masked else EMERALD_GREEN

        # Card 2: Primary Subject Loitering Time & Score
        loiter_sec = 0
        loiter_pts = 0
        if highest_person and not has_member and getattr(highest_person, "identity", "Unknown") == "Unknown":
            score_map = getattr(highest_person, "score_breakdown", {})
            loiter_pts = int(score_map.get("loitering", score_map.get("Loitering", getattr(highest_person, "loiter_score", 0))))
            loiter_sec = int(getattr(highest_person, "visible_time", getattr(highest_person, "loiter_time", 0)))

        # Card 3: Active DoorCams
        cam_title = "Active DoorCams"
        cam_val = "1 / 1"
        cam_sub = "100% System Online"
        cam_color = EMERALD_GREEN

        # Card 4: Weapon Status (Red DETECTED if Weapon present, Green NONE)
        has_weapon = False
        w_sub_str = ""
        if highest_person:
            has_weapon = getattr(highest_person, "weapon_detected", False)
            d_weapons = getattr(highest_person, "detected_weapons", [])
            if has_weapon and d_weapons:
                w_sub_str = f" ({d_weapons[0]})"
            elif not has_weapon:
                score_map = getattr(highest_person, "score_breakdown", {})
                reasons = getattr(highest_person, "threat_reasons", [])
                has_weapon = (score_map.get("weapon", 0) > 0) or (score_map.get("Weapon", 0) > 0) or any("Weapon Detected" in str(r) for r in reasons)

        weapon_title = "Weapon Status"
        weapon_val = f"DETECTED{w_sub_str}" if has_weapon else "NONE"
        weapon_sub = "Critical Weapon Flag" if has_weapon else "No Weapons Flagged"
        weapon_color = ALERT_CRIMSON if has_weapon else EMERALD_GREEN



        # Card 5: Current Threat Level
        threat_title = "Current Threat Level"
        threat_val = "LOW"
        threat_sub = "Normal Surveillance"
        threat_color = SAFE_COLOR
        if highest_person:
            lvl = getattr(highest_person, "threat_level", "LOW")
            threat_val = f"{lvl} ({highest_person.threat_score})"
            threat_sub = f"Target #{highest_person.track_id}"
            threat_color = get_threat_color(lvl)

        # Render 5 Cards
        cards_data = [
            (mask_title, mask_val, mask_sub, mask_color, "simple", is_masked),
            ("Loitering Duration", loiter_sec, loiter_pts, NEON_AMBER, "loiter", (not has_member) and (loiter_pts > 0 or loiter_sec > 30)),
            (cam_title, cam_val, cam_sub, cam_color, "simple", False),  # DoorCams always check
            (weapon_title, weapon_val, weapon_sub, weapon_color, "simple", has_weapon),
            (threat_title, threat_val, threat_sub, threat_color, "simple", getattr(highest_person, "threat_level", "SAFE") in ["HIGH", "CRITICAL"]),
        ]


        for idx, item in enumerate(cards_data):
            cx = start_x + idx * (card_w + gap)
            mode_type = item[4]
            is_warning = item[5]

            self.draw_card_base(frame, cx, card_y, card_w, card_h)

            # Circle Badge Container at (cx + 35, card_y + 44)
            circle_center = (cx + 35, card_y + 44)
            
            if idx == 2:  # Active DoorCams is ALWAYS EMERALD_GREEN check
                circle_color = EMERALD_GREEN
            elif is_warning:
                circle_color = ALERT_CRIMSON if mode_type != "loiter" else NEON_AMBER
            else:
                circle_color = EMERALD_GREEN

            cv2.circle(frame, circle_center, 22, (38, 28, 22), -1)
            cv2.circle(frame, circle_center, 22, circle_color, 1)

            # Draw icon INSIDE the circle
            if is_warning:
                self.draw_warning_icon(frame, center=circle_center, size=16, color=circle_color)
            else:
                self.draw_check_icon(frame, center=circle_center, size=16, color=circle_color)

            if mode_type == "simple":
                title, val, sub, color, _, _ = item
                cv2.putText(frame, title, (cx + 70, card_y + 28), FONT, 0.40, TEXT_MUTED, 1, cv2.LINE_AA)
                cv2.putText(frame, str(val), (cx + 70, card_y + 54), FONT, 0.72, WHITE, 2, cv2.LINE_AA)
                cv2.putText(frame, sub, (cx + 70, card_y + 74), FONT, 0.35, color, 1, cv2.LINE_AA)

            elif mode_type == "loiter":
                title, sec, pts, color, _, _ = item
                cv2.putText(frame, title, (cx + 70, card_y + 28), FONT, 0.40, TEXT_MUTED, 1, cv2.LINE_AA)
                
                # Time in WHITE, score in ORANGE
                t_text = f"{sec}s"
                p_text = f" (+{pts} pts)" if pts > 0 else " (0 pts)"
                
                (tw, _), _ = cv2.getTextSize(t_text, FONT, 0.72, 2)
                cv2.putText(frame, t_text, (cx + 70, card_y + 54), FONT, 0.72, WHITE, 2, cv2.LINE_AA)
                cv2.putText(frame, p_text, (cx + 70 + tw, card_y + 54), FONT, 0.55, NEON_AMBER, 2, cv2.LINE_AA)
                
                cv2.putText(frame, "Primary Subject Loitering", (cx + 70, card_y + 74), FONT, 0.35, color, 1, cv2.LINE_AA)


    # Threat Reasons Overview Donut Chart Card (Center Container)
    def draw_threat_reasons_donut(self, frame, x, y, w, h, highest_person: PersonTrack, has_member: bool):
        x, y, w, h = int(x), int(y), int(w), int(h)
        self.draw_card_base(frame, x, y, w, h, title="Threat Reasons Overview", icon_color=HUD_CYAN)

        # Retrieve highest person score breakdown
        score_map = getattr(highest_person, "score_breakdown", {}) if highest_person else {}
        threat_score = getattr(highest_person, "threat_score", 0) if highest_person else 0
        threat_level = getattr(highest_person, "threat_level", "SAFE") if highest_person else "SAFE"
        threat_reasons = getattr(highest_person, "threat_reasons", []) if highest_person else []

        if not score_map:
            # Default empty / baseline threat representation
            score_map = {"movement": 5, "face": 5, "loitering": 5,"crowd_density": 5,"time": 5}

        # Donut Chart Positioning (Left side of card)
        donut_cx = x + 125
        donut_cy = y + 210
        r_outer = 90
        r_inner = int(r_outer * 0.58)

        total_val = float(sum(score_map.values()))
        if total_val <= 0:
            total_val = 1.0

        current_angle = -90.0
        slice_idx = 0

        # Draw outer pie slice arcs
        for key, val in score_map.items():
            sweep_angle = (float(val) / total_val) * 360.0
            if sweep_angle <= 0:
                continue

            slice_color = PIE_COLORS[slice_idx % len(PIE_COLORS)]
            cv2.ellipse(
                frame,
                (donut_cx, donut_cy),
                (r_outer, r_outer),
                0.0,
                float(current_angle),
                float(current_angle + sweep_angle),
                slice_color,
                -1,
                cv2.LINE_AA
            )
            current_angle += sweep_angle
            slice_idx += 1

        # Center hole to form Donut Chart
        cv2.circle(frame, (donut_cx, donut_cy), r_inner, CARD_BG, -1, cv2.LINE_AA)
        cv2.circle(frame, (donut_cx, donut_cy), r_inner, CARD_BORDER, 1, cv2.LINE_AA)

        # CENTER OF DONUT CHART: Score of Highest Threat Person
        score_color = get_threat_color(threat_level)
        score_str = str(threat_score)
        
        cv2.putText(
            frame,
            score_str,
            (donut_cx - (16 if len(score_str) == 2 else 24), donut_cy + 8),
            FONT,
            1.1,
            score_color,
            3,
            cv2.LINE_AA
        )
        cv2.putText(
            frame,
            "MAX THREAT",
            (donut_cx - 32, donut_cy + 28),
            FONT,
            0.34,
            TEXT_MUTED,
            1,
            cv2.LINE_AA
        )

        # Legend List (Right side of Donut Chart)
        legend_x = donut_cx + r_outer + 30
        legend_y = y + 140

        slice_idx = 0
        for key, val in score_map.items():
            slice_color = PIE_COLORS[slice_idx % len(PIE_COLORS)]
            pct = (float(val) / total_val) * 100.0
            label = key.replace("_", " ").title()[:12]

            # Legend bullet
            cv2.rectangle(frame, (legend_x, legend_y - 8), (legend_x + 10, legend_y + 2), slice_color, -1)
            cv2.rectangle(frame, (legend_x, legend_y - 8), (legend_x + 10, legend_y + 2), WHITE, 1)

            # Text label, score points, and percentage
            cv2.putText(frame, label, (legend_x + 18, legend_y), FONT, 0.40, TEXT_LIGHT, 1, cv2.LINE_AA)
            cv2.putText(frame, f"{int(val):>2} pts ({pct:.0f}%)", (legend_x + 125, legend_y), FONT, 0.38, TEXT_MUTED, 1, cv2.LINE_AA)

            legend_y += 24
            slice_idx += 1

        # Bottom Section of Card: Flagged Threat Reasons List
        reasons_y = y + 340
        cv2.line(frame, (x + 15, reasons_y), (x + w - 15, reasons_y), CARD_BORDER, 1)
        
        cv2.putText(frame, "FLAGGED REASONS & ANALYSIS", (x + 20, reasons_y + 24), FONT, 0.42, HUD_CYAN, 1, cv2.LINE_AA)
        
        reasons_list_y = reasons_y + 50
        if not threat_reasons:
            self.draw_check_icon(frame, center=(x+10, reasons_list_y-5), size=10, color=GREEN)
            cv2.putText(frame, "No suspicious intrusion indicators flagged.", (x + 20, reasons_list_y), FONT, 0.40, SAFE_COLOR, 1, cv2.LINE_AA)
        else:
            if has_member and not getattr(highest_person, "weapon_detected", False):
                text = "Family Escort Verified (SAFE)"
                self.draw_check_icon(frame, center=(x+10, reasons_list_y-5), size=10, color=GREEN)
                cv2.putText(frame, f"{text}", (x + 20, reasons_list_y), FONT, 0.40, GREEN, 1, cv2.LINE_AA)
            else:
                for reason in threat_reasons[:4]:
                    if reason != "Family Escort Verified (SAFE)":
                        self.draw_warning_icon(frame, center=(x+10, reasons_list_y-5), size=10, color=YELLOW)
                        cv2.putText(frame, f"{reason}", (x + 20, reasons_list_y), FONT, 0.40, ALERT_CRIMSON, 1, cv2.LINE_AA)
                        reasons_list_y += 26


    # Recent Alerts & Live Activity Feed Card (Right Container)
    def draw_recent_alerts(self, frame, x, y, w, h, event_logger):
        x, y, w, h = int(x), int(y), int(w), int(h)
        self.draw_card_base(frame, x, y, w, h, title="Recent Doorway Alerts", icon_color=ALERT_CRIMSON)

        if not event_logger:
            cv2.putText(frame, "No system events logged.", (x + 20, y + 60), FONT, 0.40, TEXT_MUTED, 1, cv2.LINE_AA)
            return

        recent_events = event_logger.get_recent_events(count=8)
        log_y = y + 60

        for ev in reversed(recent_events):
            t_str = ev["time"]
            msg = ev["message"]
            p_id = ev["person_id"]
            e_type = ev["type"]

            badge_color = WHITE
            if "CRITICAL" in msg or "ALERT" in e_type:
                badge_color = ALERT_CRIMSON
            elif "ENTER" in e_type or "SAVE" in e_type:
                badge_color = EMERALD_GREEN
            elif "REC" in e_type:
                badge_color = NEON_AMBER

            # Icon dot
            cv2.circle(frame, (x + 25, log_y - 4), 5, badge_color, -1)
            
            # Event title & time
            cv2.putText(frame, f"[{e_type}] ID #{p_id}", (x + 40, log_y), FONT, 0.42, TEXT_LIGHT, 1, cv2.LINE_AA)
            cv2.putText(frame, t_str, (x + w - 75, log_y), FONT, 0.35, TEXT_MUTED, 1, cv2.LINE_AA)
            
            # Event details subtext
            cv2.putText(frame, msg[:32], (x + 40, log_y + 16), FONT, 0.36, TEXT_MUTED, 1, cv2.LINE_AA)

            log_y += 44

    # Bottom Metric Cards Row (5 Cards)
    def draw_bottom_cards(self, frame, y, people, recorder, highest_person, event_logger=None):
        y = int(y)
        card_h = 240
        card_w = 360
        gap = 18
        start_x = 24

        # Card 1: Intrusion Detection (Dynamic Continuous Alert Counter)
        cx = start_x
        alert_cnt = getattr(event_logger, "alert_count", 0) if event_logger else 0
        self.draw_card_base(frame, cx, y, card_w, card_h, title="Intrusion Detection", icon_color=ALERT_CRIMSON)
        cv2.putText(frame, str(alert_cnt), (cx + 25, y + 90), FONT, 1.4, WHITE, 3, cv2.LINE_AA)
        cv2.putText(frame, "Total Alerts Triggered", (cx + 25, y + 120), FONT, 0.40, TEXT_MUTED, 1, cv2.LINE_AA)
        # Sparkline simulator
        for sx in range(0, 300, 15):
            sy1 = y + 180 + int(math.sin(sx * 0.1 + alert_cnt) * 15)
            sy2 = y + 180 + int(math.sin((sx + 15) * 0.1 + alert_cnt) * 15)
            cv2.line(frame, (cx + 25 + sx, sy1), (cx + 25 + sx + 15, sy2), ALERT_CRIMSON, 2, cv2.LINE_AA)

        # Card 2: Person Density
        cx = start_x + 1 * (card_w + gap)
        self.draw_card_base(frame, cx, y, card_w, card_h, title="Person Density", icon_color=NEON_AMBER)
        count = len(people)
        density_str = "LOW" if count <= 1 else ("MODERATE" if count <= 3 else "HIGH")
        density_color = SAFE_COLOR if count <= 1 else (NEON_AMBER if count <= 3 else ALERT_CRIMSON)
        cv2.putText(frame, density_str, (cx + 25, y + 90), FONT, 1.3, density_color, 3, cv2.LINE_AA)
        cv2.putText(frame, f"Active Targets: {count} person(s)", (cx + 25, y + 120), FONT, 0.40, TEXT_LIGHT, 1, cv2.LINE_AA)
        cv2.putText(frame, "Doorway Proximity Monitoring", (cx + 25, y + 145), FONT, 0.38, TEXT_MUTED, 1, cv2.LINE_AA)

        # Card 3: SYSTEM STATUS (Replaces Perimeter Protection)
        cx = start_x + 2 * (card_w + gap)
        self.draw_card_base(frame, cx, y, card_w, card_h, title="SYSTEM STATUS", icon_color=EMERALD_GREEN)
        status_txt = "ACTIVE" if highest_person is None else getattr(highest_person, "threat_level", "ACTIVE")
        status_color = SAFE_COLOR if highest_person is None else get_threat_color(getattr(highest_person, "threat_level", "SAFE"))
        cv2.putText(frame, status_txt, (cx + 25, y + 90), FONT, 1.3, status_color, 3, cv2.LINE_AA)
        cv2.putText(frame, "All Surveillance Zones Secured", (cx + 25, y + 120), FONT, 0.40, TEXT_LIGHT, 1, cv2.LINE_AA)
        cv2.putText(frame, "Autonomous Sentinel Engine On", (cx + 25, y + 145), FONT, 0.38, TEXT_MUTED, 1, cv2.LINE_AA)

        # Card 4: Primary Subject Telemetry
        cx = start_x + 3 * (card_w + gap)
        self.draw_card_base(frame, cx, y, card_w, card_h, title="Subject Telemetry", icon_color=HUD_CYAN)
        if highest_person:
            cv2.putText(frame, f"Target ID: #{highest_person.track_id}", (cx + 20, y + 65), FONT, 0.45, HUD_CYAN, 1, cv2.LINE_AA)
            cv2.putText(frame, f"Identity: {highest_person.identity}", (cx + 20, y + 95), FONT, 0.42, TEXT_LIGHT, 1, cv2.LINE_AA)
            cv2.putText(frame, f"Speed: {getattr(highest_person, 'speed', 0.0):.1f} px/s", (cx + 20, y + 125), FONT, 0.40, TEXT_MUTED, 1, cv2.LINE_AA)
            cv2.putText(frame, f"Facing: {getattr(highest_person, 'face_direction', 'Front')}", (cx + 20, y + 155), FONT, 0.40, TEXT_MUTED, 1, cv2.LINE_AA)
        else:
            cv2.putText(frame, "No Target Locked", (cx + 20, y + 90), FONT, 0.60, TEXT_MUTED, 1, cv2.LINE_AA)

        # Card 5: RECORDING STATUS (Turns Red & Says ON when recording, Green & Says OFF when inactive)
        cx = start_x + 4 * (card_w + gap)
        is_rec = getattr(recorder, "recording", False)
        rec_title_color = RECORDING_ACTIVE if is_rec else RECORDING_STANDBY
        self.draw_card_base(frame, cx, y, card_w, card_h, title="RECORDING STATUS", icon_color=rec_title_color)

        if is_rec:
            # RED RECORDING ACTIVE CARD WITH LIVE RECORDING TIME
            rec_sec = int(getattr(recorder, "recording_duration", getattr(recorder, "elapsed_seconds", getattr(recorder, "duration", 15.0))))
            cv2.circle(frame, (cx + 45, y + 80), 16, RECORDING_ACTIVE, -1)
            cv2.putText(frame, "ON", (cx + 80, y + 92), FONT, 1.4, RECORDING_ACTIVE, 3, cv2.LINE_AA)
            
            # Recording Time Display
            time_str = f"REC [{rec_sec:02d}s]"
            cv2.putText(frame, f"● {time_str}", (cx + 20, y + 130), FONT, 0.44, ALERT_CRIMSON, 1, cv2.LINE_AA)
            cv2.putText(frame, "Saving HD Intrusion Footage...", (cx + 20, y + 155), FONT, 0.38, TEXT_MUTED, 1, cv2.LINE_AA)
        else:
            # GREEN STANDBY CARD
            cv2.circle(frame, (cx + 45, y + 80), 16, RECORDING_STANDBY, -1)
            cv2.putText(frame, "OFF", (cx + 80, y + 92), FONT, 1.4, RECORDING_STANDBY, 3, cv2.LINE_AA)
            cv2.putText(frame, "STANDBY / MONITORING MODE", (cx + 20, y + 130), FONT, 0.42, RECORDING_STANDBY, 1, cv2.LINE_AA)
            cv2.putText(frame, "Buffer Ready for Critical Alerts", (cx + 20, y + 155), FONT, 0.38, TEXT_MUTED, 1, cv2.LINE_AA)


    # Helper to retrieve highest threat person
    def get_highest_threat_person(self, people):
        if not people:
            return None
        return max(
            people.values(),
            key=lambda p: getattr(p, "threat_score", 0),
            default=None
        )