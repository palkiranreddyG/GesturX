"""
Calibration Manager - Handles user calibration and adaptive threshold learning
"""

import json
import os
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict


@dataclass
class CalibrationData:
    """Stores calibration data for a single gesture sample."""
    gesture_name: str
    timestamp: float
    angles: Dict[str, float]
    distances: Dict[str, float]
    finger_states: Dict[str, bool]


class CalibrationManager:
    """
    Manages user calibration and adaptive threshold learning.
    
    Features:
    - Collect gesture samples for calibration
    - Calculate optimal thresholds from samples
    - Save/load calibration profiles
    - Real-time threshold adaptation
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the calibration manager.
        
        Args:
            config_path: Path to save/load calibration data
        """
        self.config_path = config_path or "calibration_data.json"
        
        # Calibration state
        self.is_calibrating = False
        self.current_calibration_gesture = None
        self.calibration_samples = []
        self.calibration_count = 0
        
        # Adaptive thresholds
        self.learned_thresholds = {
            'angle_curled': 50.0,
            'angle_extended': 90.0,
            'distance_close': 50.0,
            'distance_far': 100.0
        }
        
        # Sample collection settings
        self.required_samples = 30
        self.sample_collection_time = 2.0  # seconds
        
        # Load existing calibration if available
        self.load_calibration()
    
    def start_calibration(self, gesture_name: str):
        """
        Start collecting calibration samples for a gesture.
        
        Args:
            gesture_name: Name of the gesture to calibrate
        """
        self.is_calibrating = True
        self.current_calibration_gesture = gesture_name
        self.calibration_samples = []
        self.calibration_count = 0
        print(f"Started calibration for gesture: {gesture_name}")
        print(f"Please perform the gesture {self.required_samples} times...")
    
    def add_sample(
        self,
        angles: Dict[str, float],
        distances: Dict[str, float],
        finger_states: Dict[str, bool]
    ):
        """
        Add a calibration sample.
        
        Args:
            angles: Dictionary of finger angles
            distances: Dictionary of finger distances
            finger_states: Dictionary of finger extended states
        """
        if not self.is_calibrating:
            return
            
        sample = CalibrationData(
            gesture_name=self.current_calibration_gesture,
            timestamp=time.time(),
            angles=angles.copy(),
            distances=distances.copy(),
            finger_states=finger_states.copy()
        )
        
        self.calibration_samples.append(sample)
        self.calibration_count += 1
        
        # Check if we have enough samples
        if self.calibration_count >= self.required_samples:
            self._process_calibration()
    
    def _process_calibration(self):
        """Process collected samples and calculate optimal thresholds."""
        if not self.calibration_samples:
            return
            
        print(f"Processing {len(self.calibration_samples)} calibration samples...")
        
        # Calculate average angles for extended vs curled fingers
        extended_angles = []
        curled_angles = []
        
        for sample in self.calibration_samples:
            for finger, is_extended in sample.finger_states.items():
                angle = sample.angles.get(finger, 0)
                if is_extended:
                    extended_angles.append(angle)
                else:
                    curled_angles.append(angle)
        
        # Calculate thresholds
        if extended_angles:
            avg_extended = sum(extended_angles) / len(extended_angles)
            # Set threshold between average extended and curled angles
            if curled_angles:
                avg_curled = sum(curled_angles) / len(curled_angles)
                self.learned_thresholds['angle_extended'] = (avg_extended + avg_curled) / 2
                self.learned_thresholds['angle_curled'] = avg_curled
        
        # Calculate distance thresholds
        close_distances = []
        far_distances = []
        
        for sample in self.calibration_samples:
            thumb_index = sample.distances.get('thumb_index', 0)
            # Determine if this should be "close" or "far" based on gesture
            # This would need context from the gesture being calibrated
            close_distances.append(thumb_index)
        
        if close_distances:
            avg_distance = sum(close_distances) / len(close_distances)
            self.learned_thresholds['distance_close'] = avg_distance * 0.6
            self.learned_thresholds['distance_far'] = avg_distance * 1.2
        
        # Finish calibration
        self.is_calibrating = False
        self.current_calibration_gesture = None
        
        print("Calibration complete!")
        print(f"Learned thresholds: {self.learned_thresholds}")
        
        # Save calibration
        self.save_calibration()
    
    def cancel_calibration(self):
        """Cancel the current calibration session."""
        self.is_calibrating = False
        self.current_calibration_gesture = None
        self.calibration_samples = []
        self.calibration_count = 0
        print("Calibration cancelled.")
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get the current learned thresholds."""
        return self.learned_thresholds.copy()
    
    def set_threshold(self, key: str, value: float):
        """
        Manually set a specific threshold.
        
        Args:
            key: Threshold key (e.g., 'angle_curled')
            value: Threshold value
        """
        if key in self.learned_thresholds:
            self.learned_thresholds[key] = value
    
    def reset_thresholds(self):
        """Reset thresholds to default values."""
        self.learned_thresholds = {
            'angle_curled': 50.0,
            'angle_extended': 90.0,
            'distance_close': 50.0,
            'distance_far': 100.0
        }
        print("Thresholds reset to defaults.")
    
    def save_calibration(self, path: Optional[str] = None):
        """
        Save calibration data to file.
        
        Args:
            path: Optional custom path to save to
        """
        save_path = path or self.config_path
        
        data = {
            'thresholds': self.learned_thresholds,
            'saved_at': time.time()
        }
        
        try:
            with open(save_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Calibration saved to {save_path}")
        except Exception as e:
            print(f"Error saving calibration: {e}")
    
    def load_calibration(self, path: Optional[str] = None) -> bool:
        """
        Load calibration data from file.
        
        Args:
            path: Optional custom path to load from
            
        Returns:
            True if calibration was loaded successfully
        """
        load_path = path or self.config_path
        
        if not os.path.exists(load_path):
            return False
            
        try:
            with open(load_path, 'r') as f:
                data = json.load(f)
            
            if 'thresholds' in data:
                self.learned_thresholds.update(data['thresholds'])
                print(f"Calibration loaded from {load_path}")
                print(f"Thresholds: {self.learned_thresholds}")
                return True
        except Exception as e:
            print(f"Error loading calibration: {e}")
            
        return False
    
    def export_calibration(self, path: str) -> bool:
        """
        Export calibration data to a specific location.
        
        Args:
            path: Path to export to
            
        Returns:
            True if export was successful
        """
        try:
            self.save_calibration(path)
            return True
        except:
            return False
    
    def import_calibration(self, path: str) -> bool:
        """
        Import calibration data from a specific location.
        
        Args:
            path: Path to import from
            
        Returns:
            True if import was successful
        """
        return self.load_calibration(path)
    
    def get_calibration_status(self) -> Dict[str, Any]:
        """Get current calibration status."""
        return {
            'is_calibrating': self.is_calibrating,
            'current_gesture': self.current_calibration_gesture,
            'samples_collected': self.calibration_count,
            'samples_required': self.required_samples,
            'progress': self.calibration_count / self.required_samples if self.required_samples > 0 else 0,
            'thresholds': self.learned_thresholds.copy()
        }
