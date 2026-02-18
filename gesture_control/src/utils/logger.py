"""
Logger - Logging utilities for gesture control system
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import deque


class Logger:
    """
    Custom logger for gesture control system.
    
    Features:
    - Console and file logging
    - Gesture and action tracking
    - Statistics collection
    - JSON export support
    """
    
    def __init__(
        self,
        enabled: bool = True,
        level: str = "INFO",
        log_file: Optional[str] = "gesture_control.log",
        log_gestures: bool = True,
        log_actions: bool = True,
        log_to_json: bool = False
    ):
        """
        Initialize the logger.
        
        Args:
            enabled: Whether logging is enabled
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Path to log file (None for no file logging)
            log_gestures: Whether to log detected gestures
            log_actions: Whether to log executed actions
            log_to_json: Whether to export logs to JSON
        """
        self.enabled = enabled
        self.log_file = log_file
        self.log_gestures = log_gestures
        self.log_actions = log_actions
        self.log_to_json = log_to_json
        
        # Set up Python logger
        self.logger = logging.getLogger('GestureControl')
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
        
        # Statistics tracking
        self.gesture_history = deque(maxlen=1000)
        self.action_history = deque(maxlen=1000)
        self.session_start = time.time()
        self.stats_interval = 60  # seconds
        self.last_stats_time = time.time()
        
        # JSON log storage
        self.json_logs = []
        
    def info(self, message: str):
        """Log info message."""
        if self.enabled:
            self.logger.info(message)
            
    def debug(self, message: str):
        """Log debug message."""
        if self.enabled:
            self.logger.debug(message)
            
    def warning(self, message: str):
        """Log warning message."""
        if self.enabled:
            self.logger.warning(message)
            
    def error(self, message: str):
        """Log error message."""
        if self.enabled:
            self.logger.error(message)
    
    def log_gesture(self, gesture: str, confidence: float):
        """
        Log a detected gesture.
        
        Args:
            gesture: Gesture type
            confidence: Detection confidence
        """
        if self.enabled and self.log_gestures:
            entry = {
                'timestamp': time.time(),
                'type': 'gesture',
                'gesture': gesture,
                'confidence': confidence
            }
            self.gesture_history.append(entry)
            if self.log_to_json:
                self.json_logs.append(entry)
            self.logger.debug(f"Gesture detected: {gesture} (confidence: {confidence:.2f})")
    
    def log_action(self, action: str, success: bool = True, details: Optional[Dict] = None):
        """
        Log an executed action.
        
        Args:
            action: Action type
            success: Whether action was successful
            details: Optional additional details
        """
        if self.enabled and self.log_actions:
            entry = {
                'timestamp': time.time(),
                'type': 'action',
                'action': action,
                'success': success,
                'details': details or {}
            }
            self.action_history.append(entry)
            if self.log_to_json:
                self.json_logs.append(entry)
            status = "SUCCESS" if success else "FAILED"
            self.logger.info(f"Action: {action} - {status}")
    
    def log_fps(self, fps: float):
        """Log FPS update."""
        if self.enabled:
            self.logger.debug(f"FPS: {fps:.1f}")
    
    def log_mode_change(self, old_mode: str, new_mode: str):
        """Log control mode change."""
        if self.enabled:
            self.logger.info(f"Mode changed: {old_mode} -> {new_mode}")
    
    def log_calibration(self, gesture: str, status: str):
        """Log calibration event."""
        if self.enabled:
            self.logger.info(f"Calibration: {gesture} - {status}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current logging statistics.
        
        Returns:
            Dictionary with gesture and action statistics
        """
        current_time = time.time()
        session_duration = current_time - self.session_start
        
        # Count gestures
        gesture_counts = {}
        for entry in self.gesture_history:
            gesture = entry['gesture']
            gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1
        
        # Count actions
        action_counts = {}
        action_success = {}
        for entry in self.action_history:
            action = entry['action']
            action_counts[action] = action_counts.get(action, 0) + 1
            if entry['success']:
                action_success[action] = action_success.get(action, 0) + 1
        
        # Calculate success rates
        success_rates = {}
        for action in action_counts:
            if action in action_success:
                success_rates[action] = action_success[action] / action_counts[action]
            else:
                success_rates[action] = 0.0
        
        return {
            'session_duration': session_duration,
            'total_gestures': len(self.gesture_history),
            'total_actions': len(self.action_history),
            'gesture_counts': gesture_counts,
            'action_counts': action_counts,
            'action_success_rates': success_rates
        }
    
    def print_statistics(self):
        """Print statistics to console."""
        stats = self.get_statistics()
        
        print("\n" + "="*50)
        print("GESTURE CONTROL STATISTICS")
        print("="*50)
        
        duration = stats['session_duration']
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        print(f"Session Duration: {minutes}m {seconds}s")
        
        print(f"\nTotal Gestures Detected: {stats['total_gestures']}")
        print("Gesture Breakdown:")
        for gesture, count in stats['gesture_counts'].items():
            print(f"  {gesture}: {count}")
        
        print(f"\nTotal Actions Executed: {stats['total_actions']}")
        print("Action Breakdown:")
        for action, count in stats['action_counts'].items():
            rate = stats['action_success_rates'].get(action, 0)
            print(f"  {action}: {count} (Success rate: {rate*100:.1f}%)")
        
        print("="*50 + "\n")
    
    def export_json(self, path: str = "logs/gesture_log.json"):
        """
        Export logs to JSON file.
        
        Args:
            path: Path to export JSON file
        """
        if not self.json_logs:
            self.warning("No logs to export")
            return
            
        # Ensure directory exists
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        try:
            with open(path, 'w') as f:
                json.dump(self.json_logs, f, indent=2)
            self.info(f"Logs exported to {path}")
        except Exception as e:
            self.error(f"Failed to export logs: {e}")
    
    def clear_history(self):
        """Clear gesture and action history."""
        self.gesture_history.clear()
        self.action_history.clear()
        self.json_logs.clear()
        self.session_start = time.time()
        self.info("History cleared")


# Global logger instance
_logger = None


def get_logger(
    enabled: bool = True,
    level: str = "INFO",
    log_file: Optional[str] = "gesture_control.log",
    log_gestures: bool = True,
    log_actions: bool = True,
    log_to_json: bool = False
) -> Logger:
    """
    Get or create the global logger instance.
    
    Args:
        enabled: Whether logging is enabled
        level: Logging level
        log_file: Path to log file
        log_gestures: Whether to log gestures
        log_actions: Whether to log actions
        log_to_json: Whether to export to JSON
        
    Returns:
        Logger instance
    """
    global _logger
    
    if _logger is None:
        _logger = Logger(
            enabled=enabled,
            level=level,
            log_file=log_file,
            log_gestures=log_gestures,
            log_actions=log_actions,
            log_to_json=log_to_json
        )
    
    return _logger
