"""
Hand Tracker Module - Real-time hand landmark detection using MediaPipe
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, List, Tuple, Dict, Any


class HandTracker:
    """
    Handles real-time hand detection and landmark tracking using MediaPipe.
    
    Attributes:
        mode: Static or streaming image mode
        max_hands: Maximum number of hands to detect
        detection_confidence: Minimum detection confidence
        tracking_confidence: Minimum tracking confidence
        model_complexity: Complexity of the hand landmark model (0, 1, or 2)
    """
    
    # Landmark indices for easy reference
    LANDMARKS = {
        'WRIST': 0,
        'THUMB_CMC': 1, 'THUMB_MCP': 2, 'THUMB_IP': 3, 'THUMB_TIP': 4,
        'INDEX_FINGER_MCP': 5, 'INDEX_FINGER_PIP': 6, 'INDEX_FINGER_DIP': 7, 'INDEX_FINGER_TIP': 8,
        'MIDDLE_FINGER_MCP': 9, 'MIDDLE_FINGER_PIP': 10, 'MIDDLE_FINGER_DIP': 11, 'MIDDLE_FINGER_TIP': 12,
        'RING_FINGER_MCP': 13, 'RING_FINGER_PIP': 14, 'RING_FINGER_DIP': 15, 'RING_FINGER_TIP': 16,
        'PINKY_MCP': 17, 'PINKY_PIP': 18, 'PINKY_DIP': 19, 'PINKY_TIP': 20
    }
    
    # Finger names
    FINGERS = ['THUMB', 'INDEX_FINGER', 'MIDDLE_FINGER', 'RING_FINGER', 'PINKY']
    
    def __init__(
        self,
        static_image_mode: bool = False,
        max_hands: int = 1,
        detection_confidence: float = 0.7,
        tracking_confidence: float = 0.7,
        model_complexity: int = 1
    ):
        """
        Initialize the hand tracker with MediaPipe settings.
        
        Args:
            static_image_mode: If True, treats input as static images
            max_hands: Maximum number of hands to detect
            detection_confidence: Minimum detection confidence (0.0-1.0)
            tracking_confidence: Minimum tracking confidence (0.0-1.0)
            model_complexity: 0=Lite, 1=Full, 2=Extra Lite
        """
        self.static_image_mode = static_image_mode
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        self.model_complexity = model_complexity
        
        # Initialize MediaPipe solutions
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Create hands detector
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.static_image_mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence,
            model_complexity=self.model_complexity
        )
        
        # Results storage
        self.current_results = None
        self.landmarks = None
        self.connections = None
        self.hand_present = False
        
    def process(self, frame: np.ndarray) -> bool:
        """
        Process a frame to detect hand landmarks.
        
        Args:
            frame: Input frame in BGR format
            
        Returns:
            True if hand is detected, False otherwise
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        self.current_results = self.hands.process(frame_rgb)
        
        # Check if hand landmarks are detected
        self.hand_present = self.current_results.multi_hand_landmarks is not None
        
        if self.hand_present:
            self.landmarks = self.current_results.multi_hand_landmarks[0]
            self.connections = self.current_results.multi_hand_landmarks[0].landmark
        else:
            self.landmarks = None
            self.connections = None
            
        return self.hand_present
    
    def get_landmark(self, landmark_id: int) -> Optional[Tuple[float, float, float]]:
        """
        Get specific landmark coordinates.
        
        Args:
            landmark_id: ID of the landmark (0-20)
            
        Returns:
            Tuple of (x, y, z) coordinates normalized to [0, 1], or None if not available
        """
        if self.connections is None or landmark_id >= len(self.connections):
            return None
        lm = self.connections[landmark_id]
        return (lm.x, lm.y, lm.z)
    
    def get_landmarks_list(self) -> List[Tuple[float, float, float]]:
        """
        Get all landmarks as a list.
        
        Returns:
            List of tuples containing (x, y, z) for each landmark
        """
        if self.connections is None:
            return []
        return [(lm.x, lm.y, lm.z) for lm in self.connections]
    
    def get_finger_tip(self, finger_name: str) -> Optional[Tuple[float, float, float]]:
        """
        Get the tip position of a specific finger.
        
        Args:
            finger_name: Name of the finger ('THUMB', 'INDEX_FINGER', etc.)
            
        Returns:
            Tuple of (x, y, z) coordinates, or None if not available
        """
        landmark_map = {
            'THUMB': self.LANDMARKS['THUMB_TIP'],
            'INDEX_FINGER': self.LANDMARKS['INDEX_FINGER_TIP'],
            'MIDDLE_FINGER': self.LANDMARKS['MIDDLE_FINGER_TIP'],
            'RING_FINGER': self.LANDMARKS['RING_FINGER_TIP'],
            'PINKY': self.LANDMARKS['PINKY_TIP']
        }
        
        landmark_id = landmark_map.get(finger_name.upper())
        if landmark_id is None:
            return None
            
        return self.get_landmark(landmark_id)
    
    def get_finger_mcp(self, finger_name: str) -> Optional[Tuple[float, float, float]]:
        """
        Get the MCP (metacarpophalangeal) joint position of a specific finger.
        
        Args:
            finger_name: Name of the finger
            
        Returns:
            Tuple of (x, y, z) coordinates, or None if not available
        """
        landmark_map = {
            'THUMB': self.LANDMARKS['THUMB_CMC'],
            'INDEX_FINGER': self.LANDMARKS['INDEX_FINGER_MCP'],
            'MIDDLE_FINGER': self.LANDMARKS['MIDDLE_FINGER_MCP'],
            'RING_FINGER': self.LANDMARKS['RING_FINGER_MCP'],
            'PINKY': self.LANDMARKS['PINKY_MCP']
        }
        
        landmark_id = landmark_map.get(finger_name.upper())
        if landmark_id is None:
            return None
            
        return self.get_landmark(landmark_id)
    
    def get_finger_pip(self, finger_name: str) -> Optional[Tuple[float, float, float]]:
        """
        Get the PIP (proximal interphalangeal) joint position of a specific finger.
        
        Args:
            finger_name: Name of the finger
            
        Returns:
            Tuple of (x, y, z) coordinates, or None if not available
        """
        landmark_map = {
            'THUMB': self.LANDMARKS['THUMB_IP'],
            'INDEX_FINGER': self.LANDMARKS['INDEX_FINGER_PIP'],
            'MIDDLE_FINGER': self.LANDMARKS['MIDDLE_FINGER_PIP'],
            'RING_FINGER': self.LANDMARKS['RING_FINGER_PIP'],
            'PINKY': self.LANDMARKS['PINKY_PIP']
        }
        
        landmark_id = landmark_map.get(finger_name.upper())
        if landmark_id is None:
            return None
            
        return self.get_landmark(landmark_id)
    
    def get_wrist(self) -> Optional[Tuple[float, float, float]]:
        """Get wrist position."""
        return self.get_landmark(self.LANDMARKS['WRIST'])
    
    def draw_landmarks(
        self,
        frame: np.ndarray,
        draw_connections: bool = True,
        draw_landmarks: bool = True,
        landmark_color: Tuple[int, int, int] = (0, 255, 0),
        connection_color: Tuple[int, int, int] = (0, 255, 0),
        landmark_thickness: int = 2,
        connection_thickness: int = 1
    ) -> np.ndarray:
        """
        Draw hand landmarks on the frame.
        
        Args:
            frame: Input frame
            draw_connections: Whether to draw connections between landmarks
            draw_landmarks: Whether to draw landmark points
            landmark_color: Color for landmark points (BGR)
            connection_color: Color for connections (BGR)
            landmark_thickness: Thickness of landmark points
            connection_thickness: Thickness of connections
            
        Returns:
            Frame with drawn landmarks
        """
        if self.landmarks is None:
            return frame
            
        if draw_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                self.landmarks,
                self.mp_hands.HAND_CONNECTIONS if draw_connections else None,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style() if draw_connections else None
            )
            
        return frame
    
    def get_hand_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the detected hand.
        
        Returns:
            Dictionary containing hand information
        """
        if not self.hand_present:
            return {
                'present': False,
                'landmarks': [],
                'fingertips': {},
                'palm_center': None
            }
        
        # Calculate palm center (average of wrist and middle finger MCP)
        wrist = self.get_wrist()
        middle_mcp = self.get_finger_mcp('MIDDLE_FINGER')
        
        if wrist and middle_mcp:
            palm_center = (
                (wrist[0] + middle_mcp[0]) / 2,
                (wrist[1] + middle_mcp[1]) / 2,
                (wrist[2] + middle_mcp[2]) / 2
            )
        else:
            palm_center = None
        
        # Get all fingertip positions
        fingertips = {}
        for finger in self.FINGERS:
            tip = self.get_finger_tip(finger)
            if tip:
                fingertips[finger] = tip
        
        return {
            'present': True,
            'landmarks': self.get_landmarks_list(),
            'fingertips': fingertips,
            'palm_center': palm_center,
            'wrist': wrist
        }
    
    def release(self):
        """Release resources."""
        if self.hands:
            self.hands.close()
