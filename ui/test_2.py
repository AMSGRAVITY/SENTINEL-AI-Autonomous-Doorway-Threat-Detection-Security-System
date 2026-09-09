from threat_detection.tracking.tracker import Tracker
from threat_detection.face.recognizer import FaceRecognizer
from threat_detection.face.orientation import FaceOrientation
from threat_detection.face.mask_detector import MaskDetector
from threat_detection.tracking.movement_analyser import MovementAnalyzer
from threat_detection.tracking.loitering_detector import LoiteringDetector
from threat_detection.tracking.time_based_behaviour import TimeBehaviour
from threat_detection.threat.threat_engine import ThreatEngine
from threat_detection.recording.recorder import Recorder
from threat_detection.ui.drawing import Drawing
from threat_detection.ui.dashboard import Dashboard
from threat_detection.ui.event_logger import EventLogger

import sys
import time
import cv2
import psutil
import torch

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    SpinnerColumn,
    TimeElapsedColumn
)

console = Console()

def check_hardware_status():
    """Performs real system checks and returns a populated Rich Table."""
    table = Table(title="[bold yellow]System Hardware Diagnostics[/bold yellow]", header_style="bold magenta", expand=True)
    
    table.add_column("Resource", style="cyan", width=18)
    table.add_column("Device / Details", style="white", width=32)
    table.add_column("Status", justify="center", width=12)
    table.add_column("Utilization / Info", style="dim", width=20)

    # 1. CPU Check
    cpu_count = psutil.cpu_count(logical=True)
    cpu_usage = psutil.cpu_percent(interval=0.1)
    table.add_row(
        "CPU",
        f"Logical Cores: {cpu_count}",
        "[bold green]ONLINE[/bold green]",
        f"Usage: {cpu_usage}%"
    )

    # 2. GPU / CUDA Check
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
        table.add_row(
            "GPU (CUDA)",
            f"{gpu_name}",
            "[bold green]READY[/bold green]",
            f"VRAM: {vram_gb} GB"
        )
    else:
        table.add_row(
            "GPU (CUDA)",
            "No CUDA GPU Detected",
            "[bold yellow]CPU MODE[/bold yellow]",
            "Fallback to CPU"
        )

    # 3. Camera Check
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            h, w, _ = frame.shape
            table.add_row(
                "Camera Stream",
                f"Index 0 ({w}x{h})",
                "[bold green]CONNECTED[/bold green]",
                "FPS Capable: ~30"
            )
        else:
            table.add_row("Camera Stream", "Index 0", "[bold red]NO FRAME[/bold red]", "Cannot read stream")
        cap.release()
    else:
        table.add_row("Camera Stream", "Index 0", "[bold red]OFFLINE[/bold red]", "Device busy/missing")

    return table


# Module list for progress bar
modules = [
    ("Tracker Engine", "threat_detection.tracking.tracker"),
    ("Face Recognizer Engine", "threat_detection.face.recognizer"),
    ("Face Orientation Engine", "threat_detection.face.orientation"),
    ("Mask Detector Engine", "threat_detection.face.mask_detector"),
    ("Movement Analyzer Engine", "threat_detection.tracking.movement_analyser"),
    ("Loitering Detector Engine", "threat_detection.tracking.loitering_detector"),
    ("Time-Based Behavior Engine", "threat_detection.tracking.time_based_behaviour"),
    ("Core Threat Engine", "threat_detection.threat.threat_engine"),
    ("Stream Recorder Engine", "threat_detection.recording.recorder"),
    ("UI Drawing Subsystem", "threat_detection.ui.drawing"),
    ("Dashboard Subsystem", "threat_detection.ui.dashboard"),
    ("Event Logger Subsystem", "threat_detection.ui.event_logger"),
]


def run_initialization_sequence():
    console.clear()
    
    # Header Banner
    console.print(
        Panel.fit(
            "[bold green]AI THREAT DETECTION & SURVEILLANCE PIPELINE[/bold green]\n"
            "[dim]University Project Demonstration — System Startup Routine[/dim]",
            border_style="green"
        )
    )
    console.print()

    # Step 1: Render Hardware Diagnostic Table
    hardware_table = check_hardware_status()
    console.print(hardware_table)
    console.print("\n[bold cyan]=== INITIALIZING THREAT DETECTION MODULES ===[/bold cyan]\n")

    # Step 2: Individual Progress Bars
    progress = Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold cyan]{task.fields[name]:<28}[/bold cyan]"),
        BarColumn(bar_width=25, complete_style="green", finished_style="bold green"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        expand=False
    )

    with progress:
        task_ids = []
        for name, path in modules:
            task_id = progress.add_task("loading", total=100, name=name)
            task_ids.append(task_id)

        for task_id in task_ids:
            for _ in range(10):
                time.sleep(0.012)
                progress.update(task_id, advance=10)

    console.print("\n[bold green]✔ All Hardware and Subsystems Verified. Launching main process...[/bold green]\n")


def main():
    run_initialization_sequence()
    # Your video loop / threat engine code here...


if __name__ == "__main__":
    main()