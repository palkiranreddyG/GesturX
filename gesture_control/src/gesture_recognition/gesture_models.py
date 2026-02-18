"""
Gesture Models - Defines gesture types and result structures
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


class GestureType(Enum):
    """Enumeration of all supported gesture types."""
    # Basic mouse control gestures
    MOUSE_MOVE = "mouse_move"
    LEFT_CLICK = "left_click"
    RIGHT_CLICK = "right_click"
    DOUBLE_CLICK = "double_click"
    SCREENSHOT = "screenshot"
    
    # Advanced gestures
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    DRAG_START = "drag_start"
    DRAG_END = "drag_end"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    
    # Presentation mode gestures
    NEXT_SLIDE = "next_slide"
    PREV_SLIDE = "prev_slide"
    PRESENTATION_MODE = "presentation_mode"
    
    # Special gestures
    PALM_OPEN = "palm_open"
    FIST = "fist"
    PEACE_SIGN = "peace_sign"
    THUMBS_UP = "thumbs_up"
    
    # System gestures
    EXIT = "exit"
    CALIBRATE = "calibrate"
    MODE_SWITCH = "mode_switch"
    NONE = "none"


class ControlMode(Enum):
    """Control modes for different use cases."""
    MOUSE = "mouse"           # Standard mouse control
    SCROLL = "scroll"         # Scroll-focused control
    PRESENTATION = "presentation"  # Presentation control
    CUSTOM = "custom"         # User-defined custom mode


@dataclass
class GestureResult:
    """
    Contains the result of gesture classification.
    
    Attributes:
        gesture_type: The type of gesture detected
        confidence: Confidence score (0.0 to 1.0)
        position: Optional position data (x, y) for mouse movement
        additional_data: Optional additional gesture-specific data
        debounce_triggered: Whether debounce was triggered
    """
    gesture_type: GestureType
    confidence: float
    position: Optional[tuple] = None
    additional_data: Optional[Dict[str, Any]] = None
    debounce_triggered: bool = False
    
    def __post_init__(self):
        """Validate and clamp values."""
        self.confidence = max(0.0, min(1.0, self.confidence))
    
    @property
    def is_click(self) -> bool:
        """Check if this is a click gesture."""
        return self.gesture_type in [
            GestureType.LEFT_CLICK,
            GestureType.RIGHT_CLICK,
            GestureType.DOUBLE_CLICK
        ]
    
    @property
    def is_movement(self) -> bool:
        """Check if this is a movement gesture."""
        return self.gesture_type == GestureType.MOUSE_MOVE
    
    @property
    def is_scrolling(self) -> bool:
        """Check if this is a scrolling gesture."""
        return self.gesture_type in [
            GestureType.SCROLL_UP,
            GestureType.SCROLL_DOWN
        ]


@dataclass
class GestureConfig:
    """
    Configuration for gesture detection thresholds and parameters.
    
    Attributes:
        angle_threshold: Threshold for angle-based detection
        distance_threshold: Threshold for distance-based detection
        confidence_threshold: Minimum confidence to trigger action
        debounce_time: Time in milliseconds to debounce gestures
    """
    angle_threshold: float = 50.0
    distance_threshold: float = 50.0
    confidence_threshold: float = 0.7
    debounce_time: int = 300
    
    # Extended finger thresholds
    finger_extended_angle: float = 90.0
    finger_curled_angle: float = 50.0
    
    # Distance thresholds for different gestures
    thumb_index_close: float = 50.0
    thumb_index_far: float = 100.0
    
    # Movement thresholds
    movement_sensitivity: float = 0.02
    
    # Scroll sensitivity
    scroll_sensitivity: float = 3.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'angle_threshold': self.angle_threshold,
            'distance_threshold': self.distance_threshold,
            'confidence_threshold': self.confidence_threshold,
            'debounce_time': self.debounce_time,
            'finger_extended_angle': self.finger_extended_angle,
            'finger_curled_angle': self.finger_curled_angle,
            'thumb_index_close': self.thumb_index_close,
            'thumb_index_far': self.thumb_index_far,
            'movement_sensitivity': self.movement_sensitivity,
            'scroll_sensitivity': self.scroll_sensitivity
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GestureConfig':
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class HandState:
    """
    Represents the current state of the detected hand.
    
    Attributes:
        landmarks: List of 21 hand landmarks
        fingers_extended: Which fingers are extended
        finger_distances: Distances between finger points
        finger_angles: Angles at finger joints
    """
    landmarks: List[tuple]
    fingers_extended: Dict[str, bool] = None
    finger_distances: Dict[str, float] = None
    finger_angles: Dict[str, float] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.fingers_extended is None:
            self.fingers_extended = {}
        if self.finger_distances is None:
            self.finger_distances = {}
        if self.finger_angles is None:
            self.finger_angles = {}
