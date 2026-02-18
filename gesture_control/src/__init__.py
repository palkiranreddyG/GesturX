"""
GestureControl - AI-based Hand Gesture Human-Computer Interaction System
"""

__version__ = "1.0.0"
__author__ = "GestureControl Team"

from .hand_tracking.hand_tracker import HandTracker
from .gesture_recognition.gesture_classifier import GestureClassifier
from .actions.mouse_actions import MouseController

__all__ = ['HandTracker', 'GestureClassifier', 'MouseController']
