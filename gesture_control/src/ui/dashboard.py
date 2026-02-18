"""
Dashboard - On-screen visual overlay showing gesture detection status
"""

import cv2
import numpy as np
import time
from typing import Optional, Dict, Any, List, Tuple
from collections import deque


class Dashboard:
    """
    On-screen dashboard showing gesture detection information.
    
    Features:
    - Real-time FPS display
    - Current gesture display
    - Control mode indicator
    - Confidence score visualization
    - Gesture history
    - Customizable appearance
    """
    
    def __init__(
        self,
        show_fps: bool = True,
        show_gesture: bool = True,
        show_mode: bool = True,
        show_confidence: bool = True,
        show_landmarks: bool = True,
        position = "top-left: str",
        theme: str = "dark"
    ):
        """
        Initialize the dashboard.
        
        Args:
            show_fps: Whether to show FPS counter
            show_gesture: Whether to show current gesture
            show_mode: Whether to show control mode
            show_confidence: Whether to show confidence score
            show_landmarks: Whether to show hand landmarks on frame
            position: Dashboard position ('top-left', 'top-right', 'bottom-left', 'bottom-right')
            theme: Visual theme ('dark', 'light', 'transparent')
        """
        self.show_fps = show_fps
        self.show_gesture = show_gesture
        self.show_mode = show_mode
        self.show_confidence = show_confidence
        self.show_landmarks = show_landmarks
        self.position = position
        self.theme = theme
        
        # Theme colors
        self.colors = self._get_theme_colors()
        
        # FPS tracking
        self.frame_times = deque(maxlen=30)
        self.current_fps = 0.0
        
        # Current state
        self.current_gesture = "None"
        self.current_mode = "Mouse"
        self.current_confidence = 0.0
        self.gesture_history = deque(maxlen=10)
        
        # Timing
        self.start_time = time.time()
        
    def _get_theme_colors(self) -> Dict[str, Tuple[int, int, int]]:
        """Get color palette based on theme."""
        themes = {
            'dark': {
                'background': (0, 0, 0),
                'text': (255, 255, 255),
                'accent': (0, 255, 0),
                'warning': (0, 165, 255),
                'error': (0, 0, 255),
                'border': (50, 50, 50)
            },
            'light': {
                'background': (255, 255, 255),
                'text': (0, 0, 0),
                'accent': (0, 128, 0),
                'warning': (255, 140, 0),
                'error': (255, 0, 0),
                'border': (200, 200, 200)
            },
            'transparent': {
                'background': (0, 0, 0),
                'text': (255, 255, 255),
                'accent': (0, 255, 0),
                'warning': (0, 165, 255),
                'error': (0, 0, 255),
                'border': (0, 0, 0)
            }
        }
        return themes.get(self.theme, themes['dark'])
    
    def update(
        self,
        gesture: Optional[str] = None,
        mode: Optional[str] = None,
        confidence: Optional[float] = None,
        frame: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Update dashboard with new information and draw on frame.
        
        Args:
            gesture: Current detected gesture
            mode: Current control mode
            confidence: Confidence score (0.0 to 1.0)
            frame: Video frame to draw on
            
        Returns:
            Frame with dashboard overlay
        """
        # Update FPS
        self.frame_times.append(time.time())
        if len(self.frame_times) > 1:
            elapsed = self.frame_times[-1] - self.frame_times[0]
            self.current_fps = (len(self.frame_times) - 1) / elapsed if elapsed > 0 else 0
        
        # Update current values
        if gesture:
            self.current_gesture = gesture
            self.gesture_history.append(gesture)
        if mode:
            self.current_mode = mode
        if confidence is not None:
            self.current_confidence = confidence
            
        # Draw on frame if provided
        if frame is not None:
            return self._draw_dashboard(frame)
            
        return None
    
    def _draw_dashboard(self, frame: np.ndarray) -> np.ndarray:
        """Draw the dashboard overlay on the frame."""
        h, w = frame.shape[:2]
        
        # Create dashboard panel
        panel_width = 250
        panel_height = 200
        panel_x, panel_y = self._get_panel_position(w, h, panel_width, panel_height)
        
        # Draw panel background
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (panel_x, panel_y),
            (panel_x + panel_width, panel_y + panel_height),
            self.colors['background'],
            -1
        )
        
        # Apply transparency if using transparent theme
        if self.theme == 'transparent':
            alpha = 0.6
            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        else:
            frame = overlay
            
        # Draw border
        cv2.rectangle(
            frame,
            (panel_x, panel_y),
            (panel_x + panel_width, panel_y + panel_height),
            self.colors['border'],
            2
        )
        
        # Draw information
        y_offset = panel_y + 30
        line_height = 25
        
        # Title
        self._draw_text(
            frame,
            "GestureControl",
            panel_x + 10,
            y_offset,
            font_scale=0.7,
            color=self.colors['accent'],
            thickness=2
        )
        y_offset += line_height + 10
        
        # FPS
        if self.show_fps:
            fps_color = self._get_fps_color()
            self._draw_text(
                frame,
                f"FPS: {self.current_fps:.1f}",
                panel_x + 10,
                y_offset,
                color=fps_color
            )
            y_offset += line_height
            
        # Current gesture
        if self.show_gesture:
            gesture_color = self._get_gesture_color()
            self._draw_text(
                frame,
                f"Gesture: {self.current_gesture}",
                panel_x + 10,
                y_offset,
                color=gesture_color
            )
            y_offset += line_height
            
        # Control mode
        if self.show_mode:
            self._draw_text(
                frame,
                f"Mode: {self.current_mode}",
                panel_x + 10,
                y_offset,
                color=self.colors['text']
            )
            y_offset += line_height
            
        # Confidence
        if self.show_confidence:
            conf_color = self._get_confidence_color()
            self._draw_text(
                frame,
                f"Confidence: {self.current_confidence:.2f}",
                panel_x + 10,
                y_offset,
                color=conf_color
            )
            y_offset += line_height
            
        # Gesture hint panel (right side)
        self._draw_gesture_hints(frame, w, h)
        
        return frame
    
    def _draw_gesture_hints(self, frame: np.ndarray, w: int, h: int):
        """Draw gesture hints on the right side of the frame."""
        hints = [
            ("Index only → Move", "Index curled + Middle → Left Click"),
            ("Middle curled + Index → Right Click", "Index + Middle → Double Click"),
            ("Three fingers → Scroll Up", "Peace sign → Presentation Mode")
        ]
        
        panel_x = w - 280
        panel_y = h - 150
        
        # Background
        cv2.rectangle(
            frame,
            (panel_x, panel_y),
            (w - 10, h - 10),
            self.colors['background'],
            -1
        )
        
        cv2.rectangle(
            frame,
            (panel_x, panel_y),
            (w - 10, h - 10),
            self.colors['border'],
            1
        )
        
        # Draw hints
        y_offset = panel_y + 20
        for hint in hints:
            self._draw_text(frame, hint[0], panel_x + 10, y_offset, font_scale=0.4)
            y_offset += 18
            self._draw_text(frame, hint[1], panel_x + 10, y_offset, font_scale=0.4)
            y_offset += 25
    
    def _get_panel_position(self, w: int, h: int, pw: int, ph: int) -> Tuple[int, int]:
        """Get panel position based on configured position."""
        positions = {
            'top-left': (10, 10),
            'top-right': (w - pw - 10, 10),
            'bottom-left': (10, h - ph - 10),
            'bottom-right': (w - pw - 10, h - ph - 10)
        }
        return positions.get(self.position, (10, 10))
    
    def _draw_text(
        self,
        frame: np.ndarray,
        text: str,
        x: int,
        y: int,
        font_scale: float = 0.5,
        color: Tuple[int, int, int] = None,
        thickness: int = 1
    ):
        """Draw text with consistent styling."""
        if color is None:
            color = self.colors['text']
            
        cv2.putText(
            frame,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA
        )
    
    def _get_fps_color(self) -> Tuple[int, int, int]:
        """Get color based on FPS value."""
        if self.current_fps >= 25:
            return self.colors['accent']
        elif self.current_fps >= 15:
            return self.colors['warning']
        else:
            return self.colors['error']
    
    def _get_gesture_color(self) -> Tuple[int, int, int]:
        """Get color based on gesture type."""
        if self.current_gesture == "None":
            return (128, 128, 128)
        return self.colors['accent']
    
    def _get_confidence_color(self) -> Tuple[int, int, int]:
        """Get color based on confidence score."""
        if self.current_confidence >= 0.7:
            return self.colors['accent']
        elif self.current_confidence >= 0.4:
            return self.colors['warning']
        else:
            return self.colors['error']
    
    def set_theme(self, theme: str):
        """Change the dashboard theme."""
        self.theme = theme
        self.colors = self._get_theme_colors()
    
    def toggle_element(self, element: str, visible: bool):
        """Toggle visibility of dashboard elements."""
        if element == 'fps':
            self.show_fps = visible
        elif element == 'gesture':
            self.show_gesture = visible
        elif element == 'mode':
            self.show_mode = visible
        elif element == 'confidence':
            self.show_confidence = visible
        elif element == 'landmarks':
            self.show_landmarks = visible
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        return {
            'fps': self.current_fps,
            'current_gesture': self.current_gesture,
            'current_mode': self.current_mode,
            'confidence': self.current_confidence,
            'gesture_history': list(self.gesture_history),
            'uptime': time.time() - self.start_time
        }
