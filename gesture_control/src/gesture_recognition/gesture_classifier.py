"""
Gesture Classifier - Main gesture classification engine with adaptive thresholds
"""

import numpy as np
import time
from typing import List, Tuple, Optional, Dict, Any
from collections import deque

from .gesture_models import (
    GestureType, 
    GestureResult, 
    GestureConfig, 
    HandState,
    ControlMode
)


class GestureClassifier:
    """
    Advanced gesture classifier with adaptive thresholding and confidence scoring.
    
    Features:
    - Adaptive gesture engine (learns from user behavior)
    - Debounce mechanism to prevent false triggers
    - Confidence scoring for better accuracy
    - Multiple control modes support
    
    Gesture Detection Logic:
    - Uses angles between finger joints to determine finger state (extended/curled)
    - Uses distances between landmarks for additional gesture discrimination
    - Combines multiple indicators for robust detection
    """
    
    # Landmark indices for easy reference
    LANDMARK = {
        'WRIST': 0,
        'THUMB_CMC': 1, 'THUMB_MCP': 2, 'THUMB_IP': 3, 'THUMB_TIP': 4,
        'INDEX_MCP': 5, 'INDEX_PIP': 6, 'INDEX_DIP': 7, 'INDEX_TIP': 8,
        'MIDDLE_MCP': 9, 'MIDDLE_PIP': 10, 'MIDDLE_DIP': 11, 'MIDDLE_TIP': 12,
        'RING_MCP': 13, 'RING_PIP': 14, 'RING_DIP': 15, 'RING_TIP': 16,
        'PINKY_MCP': 17, 'PINKY_PIP': 18, 'PINKY_DIP': 19, 'PINKY_TIP': 20
    }
    
    def __init__(self, config: Optional[GestureConfig] = None):
        """
        Initialize the gesture classifier.
        
        Args:
            config: Gesture configuration with thresholds and parameters
        """
        self.config = config or GestureConfig()
        self.current_mode = ControlMode.MOUSE
        
        # Debounce tracking
        self.last_gesture_time = {}
        self.gesture_history = deque(maxlen=30)
        self.gesture_counts = {}
        
        # Adaptive thresholds (can be adjusted through calibration)
        self.adaptive_thresholds = {
            'angle_curled': self.config.angle_threshold,
            'angle_extended': self.config.finger_extended_angle,
            'distance_close': self.config.thumb_index_close,
            'distance_far': self.config.thumb_index_far
        }
        
        # Previous positions for movement detection
        self.previous_index_tip = None
        self.previous_thumb_tip = None
        
        # Confidence calculation
        self.confidence_weights = {
            'angle_match': 0.4,
            'distance_match': 0.3,
            'consistency': 0.3
        }
        
    def set_mode(self, mode: ControlMode):
        """Set the current control mode."""
        self.current_mode = mode
        
    def update_thresholds(self, thresholds: Dict[str, float]):
        """Update adaptive thresholds from calibration."""
        self.adaptive_thresholds.update(thresholds)
        
    def classify(
        self, 
        landmarks: List[Tuple[float, float, float]],
        index_finger_tip: Optional[Tuple[float, float, float]] = None
    ) -> GestureResult:
        """
        Classify the gesture from hand landmarks.
        
        Args:
            landmarks: List of 21 hand landmarks
            index_finger_tip: Position of index finger tip for mouse movement
            
        Returns:
            GestureResult with gesture type and confidence
        """
        if not landmarks or len(landmarks) < 21:
            return GestureResult(GestureType.NONE, 0.0)
            
        # Create hand state
        hand_state = self._analyze_hand(landmarks)
        
        # Check for debounce
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Classify based on current mode
        if self.current_mode == ControlMode.MOUSE:
            result = self._classify_mouse_mode(hand_state, index_finger_tip)
        elif self.current_mode == ControlMode.SCROLL:
            result = self._classify_scroll_mode(hand_state)
        elif self.current_mode == ControlMode.PRESENTATION:
            result = self._classify_presentation_mode(hand_state)
        else:
            result = GestureResult(GestureType.NONE, 0.0)
            
        # Apply debounce
        if result.gesture_type != GestureType.NONE:
            debounce_key = result.gesture_type.value
            last_time = self.last_gesture_time.get(debounce_key, 0)
            
            if current_time - last_time < self.config.debounce_time:
                result.debounce_triggered = True
                return result
                
            self.last_gesture_time[debounce_key] = current_time
            
        # Update history
        self.gesture_history.append(result.gesture_type)
        self._update_gesture_counts(result.gesture_type)
        
        return result
    
    def _analyze_hand(self, landmarks: List[Tuple[float, float, float]]) -> HandState:
        """
        Analyze hand landmarks to determine finger states.
        
        Args:
            landmarks: List of 21 hand landmarks
            
        Returns:
            HandState with analyzed finger information
        """
        hand_state = HandState(landmarks=landmarks)
        
        # Analyze each finger
        fingers = ['THUMB', 'INDEX_FINGER', 'MIDDLE_FINGER', 'RING_FINGER', 'PINKY']
        
        for finger in fingers:
            is_extended = self._is_finger_extended(landmarks, finger)
            hand_state.fingers_extended[finger] = is_extended
            
            # Calculate finger angles
            angle = self._get_finger_angle(landmarks, finger)
            hand_state.finger_angles[finger] = angle
            
        # Calculate distances
        hand_state.finger_distances['thumb_index'] = self._get_distance(
            landmarks[self.LANDMARK['THUMB_TIP']],
            landmarks[self.LANDMARK['INDEX_TIP']]
        )
        
        hand_state.finger_distances['thumb_middle'] = self._get_distance(
            landmarks[self.LANDMARK['THUMB_TIP']],
            landmarks[self.LANDMARK['MIDDLE_TIP']]
        )
        
        return hand_state
    
    def _is_finger_extended(self, landmarks: List[Tuple[float, float, float]], finger: str) -> bool:
        """
        Determine if a finger is extended or curled.
        Uses a better method: compares fingertip position to MCP position.
        
        Args:
            landmarks: List of hand landmarks
            finger: Name of the finger
            
        Returns:
            True if finger is extended, False if curled
        """
        # Get landmark indices for the finger
        if finger == 'THUMB':
            # For thumb, check if tip is far from MCP
            mcp = landmarks[self.LANDMARK['THUMB_MCP']]
            tip = landmarks[self.LANDMARK['THUMB_TIP']]
            # Check horizontal distance (thumb sticks out to the side)
            distance = abs(tip[0] - mcp[0])
            return distance > 0.08  # Threshold for thumb extension
            
        elif finger == 'INDEX_FINGER':
            mcp = landmarks[self.LANDMARK['INDEX_MCP']]
            tip = landmarks[self.LANDMARK['INDEX_TIP']]
            # Check vertical distance (finger sticking up)
            distance = mcp[1] - tip[1]
            
        elif finger == 'MIDDLE_FINGER':
            mcp = landmarks[self.LANDMARK['MIDDLE_MCP']]
            tip = landmarks[self.LANDMARK['MIDDLE_TIP']]
            distance = mcp[1] - tip[1]
            
        elif finger == 'RING_FINGER':
            mcp = landmarks[self.LANDMARK['RING_MCP']]
            tip = landmarks[self.LANDMARK['RING_TIP']]
            distance = mcp[1] - tip[1]
            
        elif finger == 'PINKY':
            mcp = landmarks[self.LANDMARK['PINKY_MCP']]
            tip = landmarks[self.LANDMARK['PINKY_TIP']]
            distance = mcp[1] - tip[1]
            
        else:
            return False
            
        # Finger is extended if tip is significantly above MCP (y decreases going up)
        return distance > 0.02
    
    def _get_finger_angle(self, landmarks: List[Tuple[float, float, float]], finger: str) -> float:
        """Calculate the angle at the finger's joints."""
        if finger == 'THUMB':
            mcp = landmarks[self.LANDMARK['THUMB_MCP']]
            ip = landmarks[self.LANDMARK['THUMB_IP']]
            tip = landmarks[self.LANDMARK['THUMB_TIP']]
            return self._calculate_angle(mcp, ip, tip)
        elif finger == 'INDEX_FINGER':
            return self._calculate_angle(
                landmarks[self.LANDMARK['INDEX_PIP']],
                landmarks[self.LANDMARK['INDEX_DIP']],
                landmarks[self.LANDMARK['INDEX_TIP']]
            )
        elif finger == 'MIDDLE_FINGER':
            return self._calculate_angle(
                landmarks[self.LANDMARK['MIDDLE_PIP']],
                landmarks[self.LANDMARK['MIDDLE_DIP']],
                landmarks[self.LANDMARK['MIDDLE_TIP']]
            )
        elif finger == 'RING_FINGER':
            return self._calculate_angle(
                landmarks[self.LANDMARK['RING_PIP']],
                landmarks[self.LANDMARK['RING_DIP']],
                landmarks[self.LANDMARK['RING_TIP']]
            )
        elif finger == 'PINKY':
            return self._calculate_angle(
                landmarks[self.LANDMARK['PINKY_PIP']],
                landmarks[self.LANDMARK['PINKY_DIP']],
                landmarks[self.LANDMARK['PINKY_TIP']]
            )
        return 0.0
    
    def _calculate_angle(self, a: Tuple[float, float, float], 
                        b: Tuple[float, float, float], 
                        c: Tuple[float, float, float]) -> float:
        """
        Calculate the angle at point b given three points a, b, c.
        
        Args:
            a: First point (x, y, z)
            b: Middle point (vertex of angle)
            c: Third point
            
        Returns:
            Angle in degrees
        """
        # Calculate vectors
        ba = np.array([a[0] - b[0], a[1] - b[1]])
        bc = np.array([c[0] - b[0], c[1] - b[1]])
        
        # Calculate angle using dot product
        cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-10)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.degrees(np.arccos(cos_angle))
        
        return angle
    
    def _get_distance(self, p1: Tuple[float, float, float], 
                      p2: Tuple[float, float, float]) -> float:
        """Calculate Euclidean distance between two points."""
        return np.hypot(p2[0] - p1[0], p2[1] - p1[1])
    
    def _classify_mouse_mode(
        self, 
        hand_state: HandState,
        index_finger_tip: Optional[Tuple[float, float, float]]
    ) -> GestureResult:
        """
        Classify gestures for mouse control mode.
        
        Gesture mapping:
        - Index extended + others curled: Mouse movement
        - Index curled + middle extended: Left click
        - Middle curled + index extended: Right click
        - All fingers except thumb extended: Scroll up
        """
        fingers = hand_state.fingers_extended
        distances = hand_state.finger_distances
        thumb_index_dist = distances.get('thumb_index', 0)
        
        # Count extended fingers
        extended_count = sum(1 for f in fingers.values() if f)
        
        # Mouse movement: Only index finger extended (ALL other fingers curled)
        if (fingers.get('INDEX_FINGER', False) and 
            extended_count == 1):
            if index_finger_tip:
                return GestureResult(
                    GestureType.MOUSE_MOVE,
                    confidence=0.9,
                    position=(index_finger_tip[0], index_finger_tip[1])
                )
        
        # Left click: Index curled + Middle extended + Ring+Pinky curled
        if (not fingers.get('INDEX_FINGER', True) and 
            fingers.get('MIDDLE_FINGER', False) and
            not fingers.get('RING_FINGER', True) and
            not fingers.get('PINKY', True)):
            confidence = self._calculate_confidence(
                angle_match=0.85,
                distance_match=0.9,
                consistency=self._get_consistency(GestureType.LEFT_CLICK)
            )
            return GestureResult(GestureType.LEFT_CLICK, confidence)
        
        # Right click: Middle curled + Index extended + Ring+Pinky curled
        if (fingers.get('INDEX_FINGER', False) and 
            not fingers.get('MIDDLE_FINGER', True) and
            not fingers.get('RING_FINGER', True) and
            not fingers.get('PINKY', True)):
            confidence = self._calculate_confidence(
                angle_match=0.85,
                distance_match=0.9,
                consistency=self._get_consistency(GestureType.RIGHT_CLICK)
            )
            return GestureResult(GestureType.RIGHT_CLICK, confidence)
        
        # Scroll up: Index + Middle + Ring extended + Pinky curled
        if (fingers.get('INDEX_FINGER', False) and 
            fingers.get('MIDDLE_FINGER', False) and
            fingers.get('RING_FINGER', False) and
            not fingers.get('PINKY', True)):
            confidence = self._calculate_confidence(
                angle_match=0.75,
                distance_match=0.8,
                consistency=self._get_consistency(GestureType.SCROLL_UP)
            )
            return GestureResult(GestureType.SCROLL_UP, confidence)
        
        # Scroll down: Index + Middle extended + Ring+Pinky curled + hand lower
        if (fingers.get('INDEX_FINGER', False) and 
            fingers.get('MIDDLE_FINGER', False) and
            not fingers.get('RING_FINGER', True) and
            not fingers.get('PINKY', True)):
            # Get middle finger position to determine scroll direction
            middle_tip = hand_state.landmarks[self.LANDMARK['MIDDLE_TIP']]
            if middle_tip[1] > 0.6:  # Lower part of frame = scroll down
                confidence = self._calculate_confidence(
                    angle_match=0.75,
                    distance_match=0.8,
                    consistency=self._get_consistency(GestureType.SCROLL_DOWN)
                )
                return GestureResult(GestureType.SCROLL_DOWN, confidence)
            
        # Default: No gesture detected
        return GestureResult(GestureType.NONE, 0.0)
    
    def _classify_scroll_mode(self, hand_state: HandState) -> GestureResult:
        """Classify gestures for scroll mode."""
        fingers = hand_state.fingers_extended
        distances = hand_state.finger_distances
        thumb_index_dist = distances.get('thumb_index', 0)
        
        # Scroll up: Palm facing camera, fingers spread
        if (fingers.get('INDEX_FINGER', False) and 
            fingers.get('MIDDLE_FINGER', False)):
            # Determine scroll direction based on hand position
            middle_tip = hand_state.landmarks[self.LANDMARK['MIDDLE_TIP']]
            if middle_tip[1] < 0.5:  # Upper part of frame
                return GestureResult(GestureType.SCROLL_UP, 0.8)
            else:
                return GestureResult(GestureType.SCROLL_DOWN, 0.8)
                
        return GestureResult(GestureType.NONE, 0.0)
    
    def _classify_presentation_mode(self, hand_state: HandState) -> GestureResult:
        """Classify gestures for presentation mode."""
        fingers = hand_state.fingers_extended
        
        # Next slide: Index finger pointing right
        if fingers.get('INDEX_FINGER', False) and not fingers.get('MIDDLE_FINGER', True):
            return GestureResult(GestureType.NEXT_SLIDE, 0.85)
            
        # Previous slide: Index finger pointing left
        # (direction would be determined by actual finger position)
        
        return GestureResult(GestureType.NONE, 0.0)
    
    def _calculate_confidence(
        self, 
        angle_match: float, 
        distance_match: float, 
        consistency: float
    ) -> float:
        """Calculate overall confidence from individual components."""
        return (
            angle_match * self.confidence_weights['angle_match'] +
            distance_match * self.confidence_weights['distance_match'] +
            consistency * self.confidence_weights['consistency']
        )
    
    def _get_consistency(self, gesture_type: GestureType) -> float:
        """Get consistency score based on gesture history."""
        recent_gestures = list(self.gesture_history)[-5:]
        if not recent_gestures:
            return 0.5
            
        matches = sum(1 for g in recent_gestures if g == gesture_type)
        return matches / len(recent_gestures)
    
    def _update_gesture_counts(self, gesture_type: GestureType):
        """Update gesture occurrence counts."""
        key = gesture_type.value
        self.gesture_counts[key] = self.gesture_counts.get(key, 0) + 1
    
    def get_gesture_statistics(self) -> Dict[str, Any]:
        """Get statistics about gesture usage."""
        total = sum(self.gesture_counts.values())
        if total == 0:
            return {}
            
        return {
            gesture: count / total 
            for gesture, count in self.gesture_counts.items()
        }
    
    def reset_statistics(self):
        """Reset gesture statistics."""
        self.gesture_counts.clear()
        self.gesture_history.clear()
        self.last_gesture_time.clear()
