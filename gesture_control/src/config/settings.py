"""
Settings - Configuration management with YAML support
"""

import os
import yaml
import json
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class HandTrackingConfig:
    """Configuration for hand tracking."""
    static_image_mode: bool = False
    max_hands: int = 1
    detection_confidence: float = 0.7
    tracking_confidence: float = 0.7
    model_complexity: int = 1


@dataclass
class GestureConfig:
    """Configuration for gesture recognition."""
    angle_threshold: float = 50.0
    distance_threshold: float = 50.0
    confidence_threshold: float = 0.7
    debounce_time: int = 300
    finger_extended_angle: float = 90.0
    finger_curled_angle: float = 50.0
    thumb_index_close: float = 50.0
    thumb_index_far: float = 100.0
    movement_sensitivity: float = 0.02
    scroll_sensitivity: float = 3.0


@dataclass
class MouseConfig:
    """Configuration for mouse control."""
    movement_speed: float = 1.0
    scroll_speed: float = 3.0
    smoothing: bool = True
    smoothing_factor: float = 0.3


@dataclass
class UIConfig:
    """Configuration for UI dashboard."""
    show_fps: bool = True
    show_gesture: bool = True
    show_mode: bool = True
    show_confidence: bool = True
    show_landmarks: bool = True
    position: str = "top-left"
    theme: str = "dark"


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    enabled: bool = True
    level: str = "INFO"
    log_file: Optional[str] = "gesture_control.log"
    log_gestures: bool = True
    log_actions: bool = True
    log_to_json: bool = False
    log_stats_interval: int = 60  # seconds


@dataclass
class Settings:
    """
    Main settings class containing all configuration options.
    
    Attributes:
        hand_tracking: Hand tracking configuration
        gesture: Gesture recognition configuration
        mouse: Mouse control configuration
        ui: UI dashboard configuration
        logging: Logging configuration
        camera_id: Camera device ID
        frame_width: Frame width for capture
        frame_height: Frame height for capture
    """
    hand_tracking: HandTrackingConfig = field(default_factory=HandTrackingConfig)
    gesture: GestureConfig = field(default_factory=GestureConfig)
    mouse: MouseConfig = field(default_factory=MouseConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Camera settings
    camera_id: int = 0
    frame_width: int = 1280
    frame_height: int = 720
    
    # Control modes
    default_mode: str = "mouse"
    available_modes: list = field(default_factory=lambda: ["mouse", "scroll", "presentation"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            'hand_tracking': asdict(self.hand_tracking),
            'gesture': asdict(self.gesture),
            'mouse': asdict(self.mouse),
            'ui': asdict(self.ui),
            'logging': asdict(self.logging),
            'camera_id': self.camera_id,
            'frame_width': self.frame_width,
            'frame_height': self.frame_height,
            'default_mode': self.default_mode,
            'available_modes': self.available_modes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        """Create settings from dictionary."""
        return cls(
            hand_tracking=HandTrackingConfig(**data.get('hand_tracking', {})),
            gesture=GestureConfig(**data.get('gesture', {})),
            mouse=MouseConfig(**data.get('mouse', {})),
            ui=UIConfig(**data.get('ui', {})),
            logging=LoggingConfig(**data.get('logging', {})),
            camera_id=data.get('camera_id', 0),
            frame_width=data.get('frame_width', 1280),
            frame_height=data.get('frame_height', 720),
            default_mode=data.get('default_mode', 'mouse'),
            available_modes=data.get('available_modes', ["mouse", "scroll", "presentation"])
        )


def load_settings(path: str = "config/config.yaml") -> Settings:
    """
    Load settings from YAML or JSON file.
    
    Args:
        path: Path to the configuration file
        
    Returns:
        Settings object with loaded configuration
    """
    if not os.path.exists(path):
        # Return default settings if file doesn't exist
        print(f"Config file not found: {path}, using defaults")
        return Settings()
    
    try:
        with open(path, 'r') as f:
            if path.endswith('.yaml') or path.endswith('.yml'):
                data = yaml.safe_load(f)
            elif path.endswith('.json'):
                data = json.load(f)
            else:
                # Try YAML first, then JSON
                try:
                    f.seek(0)
                    data = yaml.safe_load(f)
                except:
                    f.seek(0)
                    data = json.load(f)
        
        return Settings.from_dict(data)
        
    except Exception as e:
        print(f"Error loading config: {e}")
        return Settings()


def save_settings(settings: Settings, path: str = "config/config.yaml"):
    """
    Save settings to YAML or JSON file.
    
    Args:
        settings: Settings object to save
        path: Path to save the configuration file
    """
    # Ensure directory exists
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    try:
        data = settings.to_dict()
        
        with open(path, 'w') as f:
            if path.endswith('.yaml') or path.endswith('.yml'):
                yaml.dump(data, f, default_flow_style=False, indent=2)
            elif path.endswith('.json'):
                json.dump(data, f, indent=2)
            else:
                # Default to YAML
                yaml.dump(data, f, default_flow_style=False, indent=2)
                
        print(f"Settings saved to {path}")
        
    except Exception as e:
        print(f"Error saving config: {e}")


def create_default_config(path: str = "config/config.yaml"):
    """
    Create a default configuration file.
    
    Args:
        path: Path where to create the config file
    """
    settings = Settings()
    save_settings(settings, path)
    print(f"Default configuration created at {path}")


# Default configuration as YAML string for reference
DEFAULT_CONFIG_YAML = """
# GestureControl Configuration File

# Hand Tracking Settings
hand_tracking:
  static_image_mode: false
  max_hands: 1
  detection_confidence: 0.7
  tracking_confidence: 0.7
  model_complexity: 1

# Gesture Recognition Settings
gesture:
  angle_threshold: 50.0
  distance_threshold: 50.0
  confidence_threshold: 0.7
  debounce_time: 300
  finger_extended_angle: 90.0
  finger_curled_angle: 50.0
  thumb_index_close: 50.0
  thumb_index_far: 100.0
  movement_sensitivity: 0.02
  scroll_sensitivity: 3.0

# Mouse Control Settings
mouse:
  movement_speed: 1.0
  scroll_speed: 3.0
  smoothing: true
  smoothing_factor: 0.3

# UI Dashboard Settings
ui:
  show_fps: true
  show_gesture: true
  show_mode: true
  show_confidence: true
  show_landmarks: true
  position: "top-left"
  theme: "dark"

# Logging Settings
logging:
  enabled: true
  level: "INFO"
  log_file: "gesture_control.log"
  log_gestures: true
  log_actions: true
  log_to_json: false
  log_stats_interval: 60

# Camera Settings
camera_id: 0
frame_width: 1280
frame_height: 720

# Control Modes
default_mode: "mouse"
available_modes:
  - "mouse"
  - "scroll"
  - "presentation"
"""
