from datetime import datetime
from threat_detection.core.person_track import PersonTrack
from threat_detection.config import SUBJECT

class EmailTemplate:
    def __init__(self):
        pass

    def subject(self):
        return SUBJECT

    def timestamp(self):
        return datetime.now().strftime("%d-%b-%Y %H:%M:%S")

    def consolidated_body(
        self,
        highest_person: PersonTrack,
        total_people: int = 0,
        critical_count: int = 0,
        stage: str = "immediate",
        duration_sec: float = 0.0
    ) -> str:
        
        # ------------------------------------------------------------------
        # STAGE 1: IMMEDIATE ALERT (Focus on Active Target)
        # ------------------------------------------------------------------
        if stage == "immediate":
            header = "CRITICAL SECURITY ALERT (IMMEDIATE ACTION REQUIRED)"
            
            body = f"{header}\n"
            body += "=" * 50 + "\n"
            body += f"Total People in Scene       : {total_people}\n"
            body += f"Critical Threats Identified  : {critical_count}\n"
            body += "=" * 50 + "\n\n"

            if highest_person:
                w_detected = getattr(highest_person, "weapon_detected", False)
                w_list = getattr(highest_person, "detected_weapons", [])
                w_str = f"YES ({', '.join(w_list)})" if (w_detected and w_list) else ("YES" if w_detected else "NO")
                reasons_list = getattr(highest_person, "threat_reasons", [])
                reasons_str = ", ".join(reasons_list) if reasons_list else "None"

                body += "PRIMARY TARGET DETAILS (Highest Threat):\n"
                body += f"• Track ID          : #{getattr(highest_person, 'track_id', 'N/A')}\n"
                body += f"• Identity          : {getattr(highest_person, 'identity', 'Unknown')}\n"
                body += f"• Threat Score      : {getattr(highest_person, 'threat_score', 'N/A')}\n"
                body += f"• Weapon Status     : {w_str}\n"
                body += f"• Threat Reasons    : {reasons_str}\n"
                body += f"• Loitering Score   : {getattr(highest_person, 'loitering_score', 0)}\n"
                body += f"• Movement Score    : {getattr(highest_person, 'movement_score', 0)}\n"
                body += f"• Direction Changes : {getattr(highest_person, 'direction_changes', 0)}\n\n"


            body += "Immediate snapshot attached. Full video recording will follow once the incident ends.\n"
            return body

        # ------------------------------------------------------------------
        # STAGE 2: FOLLOW-UP SUMMARY (Focus on Event Resolution & Video)
        # ------------------------------------------------------------------
        else:
            header = "INCIDENT RESOLVED - RECORDING ATTACHED"
            
            body = f"{header}\n"
            body += "=" * 50 + "\n"
            body += f"Incident Status             : Threat Subsided (Normal Level Restored)\n"
            if duration_sec > 0:
                body += f"Recording Duration          : {duration_sec:.1f} seconds\n"
            if highest_person:
                body += f"Primary Subject Tracked     : Person #{getattr(highest_person, 'track_id', 'N/A')} ({getattr(highest_person, 'identity', 'Unknown')})\n"
            body += "=" * 50 + "\n\n"

            body += "SUMMARY:\n"
            body += "• The elevated threat activity has ended and the scene has stabilized.\n"
            body += "• The full event video footage has been attached to this email for audit and archival.\n\n"
            
            body += "Attachment: Full Event Video Clip (.mp4)\n"
            return body
        

    def format_reasons(self, person: PersonTrack):
        if not person.threat_reasons:
            return None

        return "\n".join(f"• {reason}" for reason in person.threat_reasons)