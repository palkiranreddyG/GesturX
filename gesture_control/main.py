"""
GestureControl - Main Entry Point
AI-based Hand Gesture Human-Computer Interaction System

A next-generation gesture control system using Python, OpenCV, MediaPipe, and PyAutoGUI.
Features real-time hand tracking, adaptive gesture recognition, and multiple control modes.

Usage:
    python main.py              # Run with default settings
    python main.py --config    # Run with configuration file
    python main.py --calibrate # Run calibration mode
    python main.py --help      # Show help message
"""

import cv2
import argparse
import sys
import os
import time
import signal

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.hand_tracking.hand_tracker import HandTracker
from src.gesture_recognition.gesture_classifier import GestureClassifier
from src.gesture_recognition.gesture_models import GestureConfig, ControlMode, GestureType
from src.actions.mouse_actions import MouseController
from src.ui.dashboard import Dashboard
from src.calibration.calibration import CalibrationManager
from src.config.settings import Settings, load_settings, create_default_config
from src.utils.logger import Logger, get_logger


class GestureControlApp:
    """
    Main application class for GestureControl.
    
    Coordinates all components:
    - Hand tracking (MediaPipe)
    - Gesture classification
    - Mouse actions
    - UI dashboard
    - Calibration
    - Logging
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the GestureControl application.
        
        Args:
            config_path: Path to configuration file
        """
        # Load settings
        if config_path and os.path.exists(config_path):
            self.settings = load_settings(config_path)
        else:
            # Try default path
            default_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
            if os.path.exists(default_path):
                self.settings = load_settings(default_path)
            else:
                print("Config file not found, creating default configuration...")
                self.settings = Settings()
                create_default_config(default_path)
        
        # Initialize logger
        self.logger = get_logger(
            enabled=self.settings.logging.enabled,
            level=self.settings.logging.level,
            log_file=self.settings.logging.log_file,
            log_gestures=self.settings.logging.log_gestures,
            log_actions=self.settings.logging.log_actions,
            log_to_json=self.settings.logging.log_to_json
        )
        
        self.logger.info("="*50)
        self.logger.info("GestureControl Starting...")
        self.logger.info("="*50)
        
        # Initialize components
        self._init_components()
        
        # State
        self.running = False
        self.current_mode = ControlMode.MOUSE
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _init_components(self):
        """Initialize all system components."""
        # Hand tracker
        self.hand_tracker = HandTracker(
            static_image_mode=self.settings.hand_tracking.static_image_mode,
            max_hands=self.settings.hand_tracking.max_hands,
            detection_confidence=self.settings.hand_tracking.detection_confidence,
            tracking_confidence=self.settings.hand_tracking.tracking_confidence,
            model_complexity=self.settings.hand_tracking.model_complexity
        )
        
        # Gesture classifier
        gesture_config = GestureConfig(
            angle_threshold=self.settings.gesture.angle_threshold,
            distance_threshold=self.settings.gesture.distance_threshold,
            confidence_threshold=self.settings.gesture.confidence_threshold,
            debounce_time=self.settings.gesture.debounce_time,
            finger_extended_angle=self.settings.gesture.finger_extended_angle,
            finger_curled_angle=self.settings.gesture.finger_curled_angle,
            thumb_index_close=self.settings.gesture.thumb_index_close,
            thumb_index_far=self.settings.gesture.thumb_index_far,
            movement_sensitivity=self.settings.gesture.movement_sensitivity,
            scroll_sensitivity=self.settings.gesture.scroll_sensitivity
        )
        self.gesture_classifier = GestureClassifier(config=gesture_config)
        
        # Mouse controller
        self.mouse_controller = MouseController(
            movement_speed=self.settings.mouse.movement_speed,
            scroll_speed=self.settings.mouse.scroll_speed,
            smoothing=self.settings.mouse.smoothing,
            smoothing_factor=self.settings.mouse.smoothing_factor
        )
        
        # Dashboard
        self.dashboard = Dashboard(
            show_fps=self.settings.ui.show_fps,
            show_gesture=self.settings.ui.show_gesture,
            show_mode=self.settings.ui.show_mode,
            show_confidence=self.settings.ui.show_confidence,
            show_landmarks=self.settings.ui.show_landmarks,
            position=self.settings.ui.position,
            theme=self.settings.ui.theme
        )
        
        # Calibration manager
        self.calibration_manager = CalibrationManager()
        
        # Video capture
        self.cap = None
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\n\nShutting down GestureControl...")
        self.running = False
        
    def start(self):
        """Start the main application loop."""
        # Initialize camera
        self.cap = cv2.VideoCapture(self.settings.camera_id)
        
        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.frame_height)
        
        if not self.cap.isOpened():
            self.logger.error("Failed to open camera!")
            return
            
        self.logger.info("Camera opened successfully")
        self.logger.info("Starting gesture recognition...")
        
        self.running = True
        
        try:
            while self.running:
                # Read frame
                ret, frame = self.cap.read()
                if not ret:
                    self.logger.error("Failed to read frame")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process hand tracking
                hand_detected = self.hand_tracker.process(frame)
                
                # Draw landmarks if enabled
                if hand_detected and self.settings.ui.show_landmarks:
                    self.hand_tracker.draw_landmarks(frame)
                
                # Get landmarks for gesture classification
                landmarks = self.hand_tracker.get_landmarks_list()
                
                # Get index finger tip position for mouse movement
                index_finger_tip = None
                if hand_detected:
                    index_finger_tip = self.hand_tracker.get_finger_tip('INDEX_FINGER')
                
                # Classify gesture
                gesture_result = self.gesture_classifier.classify(landmarks, index_finger_tip)
                
                # Update dashboard
                self.dashboard.update(
                    gesture=gesture_result.gesture_type.value,
                    mode=self.current_mode.value,
                    confidence=gesture_result.confidence,
                    frame=frame
                )
                
                # Log gesture
                if gesture_result.gesture_type != GestureType.NONE:
                    self.logger.log_gesture(
                        gesture_result.gesture_type.value,
                        gesture_result.confidence
                    )
                
                # Execute action
                if (gesture_result.gesture_type != GestureType.NONE and 
                    not gesture_result.debounce_triggered):
                    
                    success = self.mouse_controller.execute_action(
                        gesture_result.gesture_type,
                        gesture_result.position,
                        gesture_result.additional_data
                    )
                    
                    self.logger.log_action(
                        gesture_result.gesture_type.value,
                        success
                    )
                
                # Get dashboard frame with overlay
                frame = self.dashboard._draw_dashboard(frame)
                
                # Display frame
                cv2.imshow('GestureControl', frame)
                
                # Check for key press
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    self.running = False
                elif key == ord('m') or key == 'M':
                    self._cycle_mode()
                elif key == ord('c') or key == 'C':
                    self._start_calibration()
                elif key == ord('s') or key == 'S':
                    self._toggle_smoothing()
                elif key == ord('+'):
                    self._adjust_speed(0.1)
                elif key == ord('-'):
                    self._adjust_speed(-0.1)
                    
        finally:
            self._cleanup()
            
    def _cycle_mode(self):
        """Cycle through available control modes."""
        modes = list(ControlMode)
        current_index = modes.index(self.current_mode)
        next_index = (current_index + 1) % len(modes)
        old_mode = self.current_mode.value
        self.current_mode = modes[next_index]
        self.gesture_classifier.set_mode(self.current_mode)
        self.logger.log_mode_change(old_mode, self.current_mode.value)
        
    def _start_calibration(self):
        """Start calibration mode."""
        gesture = "MOUSE_MOVE"  # Default gesture to calibrate
        self.calibration_manager.start_calibration(gesture)
        self.logger.log_calibration(gesture, "started")
        
    def _toggle_smoothing(self):
        """Toggle mouse movement smoothing."""
        current = self.mouse_controller.smoothing
        self.mouse_controller.set_smoothing(not current)
        self.logger.info(f"Smoothing {'enabled' if not current else 'disabled'}")
        
    def _adjust_speed(self, delta: float):
        """Adjust mouse movement speed."""
        new_speed = self.mouse_controller.movement_speed + delta
        new_speed = max(0.1, min(2.0, new_speed))
        self.mouse_controller.set_movement_speed(new_speed)
        self.logger.info(f"Movement speed: {new_speed:.1f}")
        
    def _cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up...")
        
        # Release camera
        if self.cap:
            self.cap.release()
            
        # Close windows
        cv2.destroyAllWindows()
        
        # Release hand tracker
        if self.hand_tracker:
            self.hand_tracker.release()
            
        # Print statistics
        self.logger.print_statistics()
        
        # Export logs if enabled
        if self.settings.logging.log_to_json:
            self.logger.export_json()
            
        self.logger.info("GestureControl stopped.")
        
    def get_status(self):
        """Get current system status."""
        return {
            'running': self.running,
            'mode': self.current_mode.value,
            'smoothing': self.mouse_controller.smoothing,
            'movement_speed': self.mouse_controller.movement_speed,
            'calibration_status': self.calibration_manager.get_calibration_status(),
            'dashboard_stats': self.dashboard.get_statistics()
        }


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='GestureControl - AI-based Hand Gesture HCI System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                      Run with default settings
  python main.py --config config.yaml  Run with custom config
  python main.py --calibrate          Start calibration mode
  python main.py --list-modes         List available control modes

Controls:
  Q           Quit the application
  M           Cycle through control modes
  C           Start calibration
  S           Toggle mouse smoothing
  +/-         Adjust mouse speed
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default=None,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--calibrate',
        action='store_true',
        help='Start in calibration mode'
    )
    
    parser.add_argument(
        '--list-modes',
        action='store_true',
        help='List available control modes and exit'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='store_true',
        help='Show version information'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Show version
    if args.version:
        print("GestureControl v1.0.0")
        print("AI-based Hand Gesture Human-Computer Interaction System")
        return
        
    # List modes
    if args.list_modes:
        print("Available Control Modes:")
        for mode in ControlMode:
            print(f"  - {mode.value}")
        return
        
    # Create and start application
    try:
        app = GestureControlApp(config_path=args.config)
        
        if args.calibrate:
            app._start_calibration()
            
        app.start()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
