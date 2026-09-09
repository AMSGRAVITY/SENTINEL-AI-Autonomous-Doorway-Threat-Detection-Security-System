from threat_detection.ui.initialization import InitializeSystem

console = InitializeSystem()

console.check_hardware_status()
console.run_initialization_sequence()