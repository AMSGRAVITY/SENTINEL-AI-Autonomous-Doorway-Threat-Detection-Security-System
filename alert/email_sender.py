import os, smtplib, mimetypes
from email.message import EmailMessage
from threat_detection.config import (
    SENDER_ADDRESS,
    SENDER_PASSWORD,
    RECIEVER_ADDRESS,
    SEND_SNAPSHOT,
    SEND_VIDEO,
    SMTP_PORT,
    SMTP_SERVER,
    SMTP_TIMEOUT,
)

class EmailSender:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT

        self.sender = SENDER_ADDRESS
        self.password = SENDER_PASSWORD

        self.receiver = RECIEVER_ADDRESS
        self.timeout = SMTP_TIMEOUT

    def attach_file(self, message: EmailMessage, filepath: str):
        if not filepath or not os.path.exists(filepath):
            return

        ctype, _ = mimetypes.guess_type(filepath)
        if ctype is None:
            ctype = "application/octet-stream"

        maintype, subtype = ctype.split("/", 1)

        with open(filepath, "rb") as f:
            data = f.read()

        filename = os.path.basename(filepath)

        message.add_attachment(
            data,
            maintype = maintype,
            subtype = subtype,
            filename = filename
        )

    def send(
            self,
            subject: str,
            body: str,
            snapshot_path: str = None,
            video_path: str = None
    ) -> bool:

        try:

            message = EmailMessage()

            message["From"] = self.sender
            message["To"] = self.receiver
            message["Subject"] = subject
            message.set_content(body)

            self.attach_file(message, snapshot_path)
            self.attach_file(message, video_path)

            with smtplib.SMTP(
                self.smtp_server,
                self.smtp_port,
                timeout=self.timeout
            ) as smtp:
                
                smtp.starttls()
                smtp.login(self.sender, self.password)
                smtp.send_message(message)

            print("[EMAIL] Alert Email sent successfully...")

            return True

        except Exception as e:
            print(f"[EMAIL ERROR] {e}")

            return False