"""
Mouse Actions - Handles all mouse and keyboard actions based on gestures
"""

import pyautogui
import random
import time
from typing import Optional, Tuple, Any, Dict
from pynput.mouse import Button, Controller

from ..gesture_recognition.gesture_models import GestureType


class MouseController:
    """
    Controls mouse and keyboard actions based on detected gestures.
    
    Features:
    - Smooth mouse movement with configurable speed
    - Left, right, and double click support
    - Scroll control
    - Drag and drop support
    - Screenshot capture
    - Configurable sensitivity and thresholds
    """
    
    def __init__(
        self,
        movement_speed: float = 1.0,
        scroll_speed: float = 3.0,
        smoothing: bool = True,
        smoothing_factor: float = 0.3
    ):
        """
        Initialize the mouse controller.
        
        Args:
            movement_speed: Speed multiplier for mouse movement (0.1 to 2.0)
            scroll_speed: Number of scroll steps per gesture
            smoothing: Whether to apply smoothing to mouse movement
            smoothing_factor: Smoothing factor (0.0 to 1.0, lower = smoother)
        """
        self.movement_speed = movement_speed
        self.scroll_speed = scroll_speed
        self.smoothing = smoothing
        self.smoothing_factor = smoothing_factor
        
        # Initialize pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01  # Small delay between actions
        
        # Initialize pynput for more precise control
        self.mouse = Controller()
        
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
        # State tracking
        self.is_dragging = False
        self.last_position = None
        self.screenshot_count = 0
        
        # Performance tracking
        self.action_counts = {}
        
    def execute_action(
        self,
        gesture_type: GestureType,
        position: Optional[Tuple[float, float]] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Execute the appropriate action based on gesture type.
        
        Args:
            gesture_type: The type of gesture to execute
            position: Optional position data (normalized 0-1) for mouse movement
            additional_data: Optional additional action-specific data
            
        Returns:
            True if action was executed, False otherwise
        """
        if gesture_type == GestureType.NONE:
            return False
            
        action_executed = False
        
        try:
            if gesture_type == GestureType.MOUSE_MOVE and position:
                self._move_mouse(position)
                action_executed = True
                
            elif gesture_type == GestureType.LEFT_CLICK:
                self._left_click()
                action_executed = True
                
            elif gesture_type == GestureType.RIGHT_CLICK:
                self._right_click()
                action_executed = True
                
            elif gesture_type == GestureType.DOUBLE_CLICK:
                self._double_click()
                action_executed = True
                
            elif gesture_type == GestureType.SCREENSHOT:
                self._take_screenshot()
                action_executed = True
                
            elif gesture_type == GestureType.SCROLL_UP:
                self._scroll_up()
                action_executed = True
                
            elif gesture_type == GestureType.SCROLL_DOWN:
                self._scroll_down()
                action_executed = True
                
            elif gesture_type == GestureType.DRAG_START:
                self._start_drag()
                action_executed = True
                
            elif gesture_type == GestureType.DRAG_END:
                self._end_drag()
                action_executed = True
                
            elif gesture_type == GestureType.ZOOM_IN:
                self._zoom_in()
                action_executed = True
                
            elif gesture_type == GestureType.ZOOM_OUT:
                self._zoom_out()
                action_executed = True
                
            elif gesture_type == GestureType.NEXT_SLIDE:
                self._next_slide()
                action_executed = True
                
            elif gesture_type == GestureType.PREV_SLIDE:
                self._prev_slide()
                action_executed = True
                
        except Exception as e:
            print(f"Error executing action {gesture_type}: {e}")
            action_executed = False
            
        # Update action counts
        if action_executed:
            key = gesture_type.value
            self.action_counts[key] = self.action_counts.get(key, 0) + 1
            
        return action_executed
    
    def _move_mouse(self, position: Tuple[float, float]):
        """
        Move mouse to specified position with smoothing.
        
        Args:
            position: Normalized position (x, y) in range 0-1
        """
        # Convert normalized position to screen coordinates
        x = int(position[0] * self.screen_width)
        y = int(position[1] * self.screen_height)
        
        # Apply movement speed
        if self.movement_speed != 1.0:
            if self.last_position:
                # Interpolate towards target
                x = int(self.last_position[0] + (x - self.last_position[0]) * self.movement_speed)
                y = int(self.last_position[1] + (y - self.last_position[1]) * self.movement_speed)
        
        # Apply smoothing
        if self.smoothing and self.last_position:
            x = int(self.last_position[0] + (x - self.last_position[0]) * self.smoothing_factor)
            y = int(self.last_position[1] + (y - self.last_position[1]) * self.smoothing_factor)
        
        # Clamp to screen bounds
        x = max(0, min(x, self.screen_width - 1))
        y = max(0, min(y, self.screen_height - 1))
        
        # Move mouse
        pyautogui.moveTo(x, y)
        
        # Update last position
        self.last_position = (x, y)
    
    def _left_click(self):
        """Execute left click."""
        self.mouse.press(Button.left)
        self.mouse.release(Button.left)
    
    def _right_click(self):
        """Execute right click."""
        self.mouse.press(Button.right)
        self.mouse.release(Button.right)
    
    def _double_click(self):
        """Execute double click."""
        pyautogui.doubleClick()
    
    def _take_screenshot(self):
        """Take a screenshot and save it."""
        timestamp = int(time.time())
        self.screenshot_count += 1
        filename = f"gesture_screenshot_{timestamp}_{self.screenshot_count}.png"
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"Screenshot saved: {filename}")
    
    def _scroll_up(self):
        """Scroll up."""
        pyautogui.scroll(self.scroll_speed)
    
    def _scroll_down(self):
        """Scroll down."""
        pyautogui.scroll(-self.scroll_speed)
    
    def _start_drag(self):
        """Start drag operation."""
        if not self.is_dragging:
            self.mouse.press(Button.left)
            self.is_dragging = True
    
    def _end_drag(self):
        """End drag operation."""
        if self.is_dragging:
            self.mouse.release(Button.left)
            self.is_dragging = False
    
    def _zoom_in(self):
        """Zoom in (platform dependent)."""
        # Use Ctrl + Plus for zoom in most applications
        pyautogui.hotkey('ctrl', 'plus')
    
    def _zoom_out(self):
        """Zoom out (platform dependent)."""
        # Use Ctrl + Minus for zoom in most applications
        pyautogui.hotkey('ctrl', 'minus')
    
    def _next_slide(self):
        """Go to next slide (commonly Right Arrow or Page Down)."""
        pyautogui.press('right')
    
    def _prev_slide(self):
        """Go to previous slide (commonly Left Arrow or Page Up)."""
        pyautogui.press('left')
    
    def set_movement_speed(self, speed: float):
        """Set mouse movement speed."""
        self.movement_speed = max(0.1, min(2.0, speed))
    
    def set_scroll_speed(self, speed: float):
        """Set scroll speed."""
        self.scroll_speed = max(1, min(10, int(speed)))
    
    def set_smoothing(self, enabled: bool, factor: float = 0.3):
        """Configure mouse movement smoothing."""
        self.smoothing = enabled
        self.smoothing_factor = max(0.0, min(1.0, factor))
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions."""
        return (self.screen_width, self.screen_height)
    
    def get_action_statistics(self) -> Dict[str, int]:
        """Get statistics about executed actions."""
        return self.action_counts.copy()
    
    def reset_statistics(self):
        """Reset action statistics."""
        self.action_counts.clear()
    
    def is_drag_active(self) -> bool:
        """Check if drag operation is active."""
        return self.is_dragging
    
    def emergency_stop(self):
        """Emergency stop - release all buttons."""
        try:
            self.mouse.release(Button.left)
            self.mouse.release(Button.right)
            self.is_dragging = False
        except:
            pass
