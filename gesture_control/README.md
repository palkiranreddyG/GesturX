# GestureControl

A next-generation AI-based Hand Gesture Human-Computer Interaction (HCI) system built with Python, OpenCV, MediaPipe, and PyAutoGUI.

## Features

### Core Features
- **Real-time Hand Tracking** - Using MediaPipe's state-of-the-art 21-landmark hand detection
- **Gesture Classification** - Advanced angle and distance-based gesture recognition
- **Mouse Control** - Move mouse cursor, left/right click with hand gestures
- **Scroll Control** - Scroll up/down with finger gestures

### Advanced Features
- **Confidence Scoring** - Provides reliability metrics for each detection
- **Gesture Debounce** - Prevents accidental multiple triggers
- **Multiple Control Modes:**
  - Mouse Mode - Standard mouse control
  - Scroll Mode - Scroll-focused control
  - Presentation Mode - Navigate slides with gestures

### UI/UX
- **On-screen Dashboard** - Real-time display of:
  - Current FPS
  - Detected gesture
  - Control mode
  - Confidence score
- **Visual Feedback** - Clear indication of current system state
- **Customizable Themes** - Dark, light, or transparent themes

### Technical Features
- **Modular Architecture** - Clean separation of concerns
- **YAML Configuration** - Easy customization without code changes
- **Comprehensive Logging** - Track gestures, actions, and system performance

## Installation

### Prerequisites
- Python 3.8 or higher
- Webcam
- A computer with moderate processing power

### Install Dependencies

```
bash
# Navigate to the project directory
cd gesture_control

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```
bash
# Run with default settings
python main.py
```

### Advanced Options

```
bash
# Run with custom configuration
python main.py --config path/to/config.yaml

# Start in calibration mode
python main.py --calibrate

# List available control modes
python main.py --list-modes

# Show help
python main.py --help
```

### Controls

| Key | Action |
|-----|--------|
| Q | Quit application |
| M | Cycle through control modes |
| C | Start calibration |
| S | Toggle mouse smoothing |
| + | Increase mouse speed |
| - | Decrease mouse speed |

## Implemented Gestures

### Mouse Mode
| Gesture | Action |
|---------|--------|
| Index finger extended (only) | Move mouse cursor |
| Index curled + Middle extended | Left click |
| Middle curled + Index extended | Right click |
| Index + Middle + Ring extended | Scroll up |

### Scroll Mode
| Gesture | Action |
|---------|--------|
| Two fingers up | Scroll up |
| Two fingers down | Scroll down |

### Presentation Mode
| Gesture | Action |
|---------|--------|
| Index pointing right | Next slide |

## Configuration

Configuration is managed through `config/config.yaml`. Key settings include:

### Hand Tracking
```
yaml
hand_tracking:
  detection_confidence: 0.7   # Higher = more strict detection
  tracking_confidence: 0.7  # Higher = more stable tracking
  model_complexity: 1        # 0=Lite, 1=Full, 2=Extra Lite
  max_hands: 1              # Maximum hands to detect
```

### Gesture Recognition
```
yaml
gesture:
  angle_threshold: 50.0       # Angle threshold for finger states
  distance_threshold: 50.0    # Distance threshold for gestures
  confidence_threshold: 0.7   # Minimum confidence to trigger action
  debounce_time: 300          # Milliseconds between gesture triggers
  finger_extended_angle: 90.0 # Angle for extended finger detection
```

### Mouse Control
```
yaml
mouse:
  movement_speed: 1.0        # Speed multiplier (0.1 to 2.0)
  scroll_speed: 3           # Scroll steps per gesture
  smoothing: true           # Apply movement smoothing
  smoothing_factor: 0.3     # Lower = smoother but slower
```

### UI Dashboard
```
yaml
ui:
  show_fps: true            # Show FPS counter
  show_gesture: true        # Show detected gesture
  show_mode: true           # Show control mode
  show_confidence: true     # Show confidence score
  show_landmarks: true      # Draw hand landmarks on video
  position: "top-left"     # Dashboard position
  theme: "dark"            # Theme: dark, light, transparent
```

### Logging
```
yaml
logging:
  enabled: true             # Enable logging
  level: "INFO"            # Log level: DEBUG, INFO, WARNING, ERROR
  log_file: "gesture_control.log"  # Log file path
  log_gestures: true       # Log detected gestures
  log_actions: true        # Log executed actions
  log_to_json: false       # Export logs to JSON
```

## Project Structure

```
gesture_control/
├── src/
│   ├── hand_tracking/       # MediaPipe hand detection
│   │   └── hand_tracker.py # Hand landmark detection
│   ├── gesture_recognition/ # Gesture classification
│   │   ├── gesture_classifier.py  # Gesture detection logic
│   │   └── gesture_models.py      # Gesture types and configs
│   ├── actions/            # Mouse/keyboard actions
│   │   └── mouse_actions.py       # Action execution
│   ├── ui/                 # Dashboard overlay
│   │   └── dashboard.py    # On-screen display
│   ├── calibration/        # User calibration
│   │   └── calibration.py  # Calibration manager
│   ├── config/             # Configuration management
│   │   └── settings.py     # Settings loader
│   └── utils/              # Logging utilities
│       └── logger.py       # Logging system
├── config/
│   └── config.yaml         # Configuration file
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── README.md               # This file
└── LICENSE                 # License
```

## Troubleshooting

### Camera not detected
- Check if camera is connected
- Try a different camera ID in config (default: 0)
- Ensure no other application is using the camera

### Gestures not detected
- Ensure good lighting
- Position hand clearly in camera view
- Make hand faces the camera (palm facing camera)
- Adjust confidence thresholds in config

### Mouse too fast/slow
- Use +/- keys to adjust speed
- Toggle smoothing with S key
- Adjust movement_speed in config

### Low FPS
- Reduce frame resolution in config
- Disable show_landmarks in config
- Use model_complexity: 0 for faster processing

## Planned Features

The following features have action handlers implemented but are not yet connected to gesture detection:
- Double click
- Screenshot capture
- Drag and drop
- Zoom in/out
- Previous slide navigation
- Multi-hand support

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for hand tracking
- [OpenCV](https://opencv.org/) for image processing
- [PyAutoGUI](https://pyautogui.readthedocs.io/) for cross-platform GUI automation
- [pynput](https://pynput.readthedocs.io/) for precise mouse control

---

Built with ❤️ for the future of human-computer interaction
