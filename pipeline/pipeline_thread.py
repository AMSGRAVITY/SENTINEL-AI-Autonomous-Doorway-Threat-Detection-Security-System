import threading, queue
from threat_detection.pipeline.pipeline_detection import DetectionPipeline

class ThreadedPipeline:
    def __init__(self):
        self.pipeline = DetectionPipeline()
        self.input_queue = queue.Queue(maxsize=1)
        self.output_queue = queue.Queue(maxsize=1)
        self.running = True
        self.latest_people = {}

        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        print("[PIPELINE] Background worker thread started...")

    def _worker(self):
        while self.running:
            try:
                frame = self.input_queue.get(timeout=0.05)
                people = self.pipeline.process(frame)
                self.latest_people = people

                if not self.output_queue.empty():
                    try:
                        self.output_queue.get_nowait()
                    except queue.Empty:
                        pass

                self.output_queue.put(people)
                self.input_queue.task_done()

            except queue.Empty:
                continue

    def process_async(self, frame):
        if self.input_queue.empty():
            self.input_queue.put(frame.copy())

    def get_latest_results(self):
        if not self.output_queue.empty():
            return self.output_queue.get_nowait()
        return self.latest_people

    def stop(self):
        self.running = False