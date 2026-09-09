import os, cv2, time, queue, threading
from collections import deque
from datetime import datetime
from threat_detection.media.recording.clip import VideoClip
from threat_detection.config import (
    RECORD_BUFFER_SEC,
    RECORD_FPS,
    RECORD_OUTPUT_PATH,
)

class ThreadedRecorder:

    def __init__(
        self,
        output_dir=RECORD_OUTPUT_PATH,
        fps=RECORD_FPS,
        buffer_seconds=RECORD_BUFFER_SEC,
        cooldown_sec=5
    ):

        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.fps = fps
        self.frame_size = None
        self.buffer = deque(maxlen=int(buffer_seconds * fps))
        self.recording = False
        self.last_threat_time = 0

        self.writer = None
        self.current_clip = None
        self.write_queue = queue.Queue(maxsize=200)
        self.running = True
        self.cooldown_sec = cooldown_sec

        self.thread = threading.Thread(target=self._disk_writer_worker, daemon=True)
        self.thread.start()

    def update(self, frame, people):
        h, w = frame.shape[:2]
        self.frame_size = (w, h)
    
        current_time = time.time()

        self.buffer.append(
            (current_time, frame.copy())
        )

        threat_detected = any(person.should_record for person in people.values())

        if threat_detected:
            self.last_threat_time = current_time
            if not self.recording:
                self.start()

        if self.recording:
            time_since_threat = current_time - self.last_threat_time
            if not threat_detected and time_since_threat >= self.cooldown_sec:
                self.stop()
            else:
                try:
                    self.write_queue.put_nowait(frame.copy())
                except queue.Full:
                    pass


    def start(self):

        if self.recording:
            return

        filename = datetime.now().strftime(
            "%Y%m%d_%H%M%S.mp4"
        )

        filepath = os.path.join(
            self.output_dir,
            filename
        )

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        self.writer = cv2.VideoWriter(
            filepath,
            fourcc,
            self.fps,
            self.frame_size
        )
        self.recording = True
        self.current_clip = VideoClip(
            filename=filepath,
            start_time=datetime.now()
        )

        # Buffered Frames

        for _, buffered_frame in list(self.buffer):
            try:
                bh, bw = buffered_frame.shape[:2]
                if (bw, bh) == self.frame_size:
                    self.write_queue.put_nowait(buffered_frame)
            except queue.Full:
                break

        print(f"[RECORDER THREAD] Started background recording: {filepath}")


    def stop(self, save=True) -> str:

        if not self.recording:
            return

        self.recording = False
        filename = self.current_clip.filename

        self.current_clip.end_time = datetime.now()

        self.current_clip.duration = (
            self.current_clip.end_time -
            self.current_clip.start_time
        ).total_seconds()

        self.write_queue.put("STOP_AND_RELEASE")
        self.write_queue.join()

        if save:

            self.current_clip.saved = True
            print(f"[RECORDER THREAD] Finalizing recording in background: {filename}")

        else:

            if os.path.exists(filename):
                os.remove(filename)

            print("[Recorder] Clip deleted")

        self.current_clip = None
        return filename

    def _disk_writer_worker(self):
        while self.running:
            try:
                item = self.write_queue.get(timeout=0.05)

                if isinstance(item, str) and item == "STOP_AND_RELEASE":
                    if self.writer is not None:
                        self.writer.release()
                        self.writer = None
                        print("[RECORDER THREAD] Video Safely saved and released")
                    self.write_queue.task_done()
                    continue
                if self.writer is not None and isinstance(item, type(None)) is False:
                    self.writer.write(item)

                self.write_queue.task_done()
            except queue.Empty:
                continue
                            

    def clear_buffer(self):
        self.buffer.clear()