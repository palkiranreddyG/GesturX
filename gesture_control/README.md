<<<<<<< HEAD
# GesturX ✋🖱️

**GesturX** is a next-generation **AI-based Hand Gesture Human–Computer Interaction (HCI) system** that enables touchless control of your computer using real-time hand gestures.

Built using **Python, OpenCV, MediaPipe, and PyAutoGUI**, GesturX transforms natural hand movements into intuitive system actions.

---

## 🚀 Features

### 🔹 Core Features
- **Real-time Hand Tracking** – Uses MediaPipe’s 21-landmark hand detection
- **Gesture Classification** – Angle and distance-based gesture recognition
- **Mouse Control** – Cursor movement, left click, right click using gestures
- **Scroll Control** – Smooth vertical scrolling via finger gestures

---

### 🔹 Advanced Features
- **Confidence Scoring** – Reliability score for each detected gesture
- **Gesture Debounce** – Prevents accidental repeated actions
- **Multiple Control Modes**
  - Mouse Mode
  - Scroll Mode
  - Presentation Mode

---

### 🔹 UI / UX
- **On-screen Dashboard**
  - FPS
  - Detected gesture
  - Current control mode
  - Confidence score
- **Visual Feedback** – Clear system state indication
- **Customizable Themes** – Dark, light, transparent

---

### 🔹 Technical Highlights
- Modular architecture
- YAML-based configuration
- Comprehensive logging system

---

## 🛠 Installation

### Prerequisites
- Python **3.8 or higher**
- Webcam
- Moderate processing power system

---

### Install Dependencies

```bash
=======
# GesturX

A next-generation AI-based **Hand Gesture Human-Computer Interaction (HCI)** system built with **Python**, **OpenCV**, **MediaPipe**, and **PyAutoGUI**.

---

## 🚀 Features

### Core Features
- **Real-time Hand Tracking** – Uses MediaPipe's 21-landmark hand detection
- **Gesture Classification** – Angle and distance-based gesture recognition
- **Mouse Control** – Cursor movement, left click, right click using gestures
- **Scroll Control** – Smooth vertical scrolling via finger gestures

### Advanced Features
- **Confidence Scoring** – Reliability score for each detected gesture
- **Gesture Debounce** – Prevents accidental repeated actions
- **Multiple Control Modes**
  - Mouse Mode
  - Scroll Mode
  - Presentation Mode

### UI / UX
- **On-screen Dashboard**
  - FPS
  - Detected gesture
  - Current control mode
  - Confidence score
- **Visual Feedback** – Clear system state indication
- **Customizable Themes** – Dark, light, transparent

### Technical Highlights
- **Modular Architecture**
- **YAML-based Configuration**
- **Comprehensive Logging System**

---

## 🛠 Installation

### Prerequisites
- **Python 3.8** or higher
- **Webcam**
- **Moderate processing power** system

### Install Dependencies

```
bash
>>>>>>> 07fe34f (Finalize README updates)
# Navigate to the project directory
cd gesturx

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows
venv\# macOS / Linux
source vScripts\activate

env/bin/activate

# Install required packages
pip install -r requirements.txt
<<<<<<< HEAD
▶️ Usage
Basic Run
python main.py
Advanced Options
=======
```

---

## ▶️ Usage

### Basic Run
```
bash
python main.py
```

### Advanced Options
```
bash
>>>>>>> 07fe34f (Finalize README updates)
python main.py --config path/to/config.yaml
python main.py --calibrate
python main.py --list-modes
python main.py --help
<<<<<<< HEAD
🎮 Controls
Key	Action
Q	Quit
M	Switch control modes
C	Start calibration
S	Toggle mouse smoothing
+	Increase cursor speed
-	Decrease cursor speed
✋ Implemented Gestures
🖱 Mouse Mode
Gesture	Action
Index finger only	Move cursor
Index curled + Middle extended	Left click
Middle curled + Index extended	Right click
Index + Middle + Ring extended	Scroll up
📜 Scroll Mode
Gesture	Action
Two fingers up	Scroll up
Two fingers down	Scroll down
🎤 Presentation Mode
Gesture	Action
Index pointing right	Next slide
⚙ Configuration
Configuration file: config/config.yaml
=======
```

---

## 🎮 Controls
>>>>>>> 07fe34f (Finalize README updates)

| Key | Action |
|-----|--------|
| **Q** | Quit |
| **M** | Switch control modes |
| **C** | Start calibration |
| **S** | Toggle mouse smoothing |
| **+** | Increase cursor speed |
| **-** | Decrease cursor speed |

---

## ✋ Implemented Gestures

### Mouse Mode

| Gesture | Action |
|---------|--------|
| Index finger only | Move cursor |
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

---

## ⚙ Configuration

**Configuration file:** `config/config.yaml`

### Hand Tracking
```
yaml
hand_tracking:
  detection_confidence: 0.7
  tracking_confidence: 0.7
  model_complexity: 1
  max_hands: 1
<<<<<<< HEAD
Gesture Recognition
=======
```

### Gesture Recognition
```
yaml
>>>>>>> 07fe34f (Finalize README updates)
gesture:
  angle_threshold: 50.0
  distance_threshold: 50.0
  confidence_threshold: 0.7
  debounce_time: 300
  finger_extended_angle: 90.0
<<<<<<< HEAD
Mouse Control
=======
```

### Mouse Control
```
yaml
>>>>>>> 07fe34f (Finalize README updates)
mouse:
  movement_speed: 1.0
  scroll_speed: 3
  smoothing: true
  smoothing_factor: 0.3
<<<<<<< HEAD
UI Dashboard
=======
```

### UI Dashboard
```
yaml
>>>>>>> 07fe34f (Finalize README updates)
ui:
  show_fps: true
  show_gesture: true
  show_mode: true
  show_confidence: true
  show_landmarks: true
  position: "top-left"
  theme: "dark"
<<<<<<< HEAD
Logging
=======
```

### Logging
```
yaml
>>>>>>> 07fe34f (Finalize README updates)
logging:
  enabled: true
  level: "INFO"
  log_file: "gesturx.log"
  log_gestures: true
  log_actions: true
  log_to_json: false
<<<<<<< HEAD
📁 Project Structure
=======
```

---

## 📁 Project Structure

```
>>>>>>> 07fe34f (Finalize README updates)
gesturx/
├── src/
│   ├── hand_tracking/
│   ├── gesture_recognition/
│   ├── actions/
│   ├── ui/
│   ├── calibration/
│   ├── config/
│   └── utils/
├── config/
├── main.py
├── requirements.txt
├── README.md
└── LICENSE
<<<<<<< HEAD
🧪 Troubleshooting
Camera Not Detected
Ensure webcam is connected
=======
```

---

## 🧪 Troubleshooting
>>>>>>> 07fe34f (Finalize README updates)

### Camera Not Detected
- Ensure webcam is connected
- Change camera ID in config (default: 0)
- Close other apps using the camera

### Gestures Not Recognized
- Improve lighting
- Keep palm facing the camera
- Adjust confidence thresholds

<<<<<<< HEAD
Gestures Not Recognized
Improve lighting
=======
### Cursor Speed Issues
- Use + / - keys
- Toggle smoothing using S
- Modify movement_speed in config

### Low FPS
- Disable landmarks
- Reduce resolution
- Use model_complexity: 0
>>>>>>> 07fe34f (Finalize README updates)

---

## 🔮 Planned Features

<<<<<<< HEAD
Cursor Speed Issues
Use + / - keys
=======
- Double click
- Screenshot capture
- Drag & drop
- Zoom in / out
- Previous slide gesture
- Multi-hand support

---
>>>>>>> 07fe34f (Finalize README updates)

## 📜 License

This project is licensed under the **MIT License**.

<<<<<<< HEAD
Low FPS
Disable landmarks
=======
---

## 🙌 Acknowledgments
>>>>>>> 07fe34f (Finalize README updates)

- **MediaPipe** – Hand tracking
- **OpenCV** – Computer vision
- **PyAutoGUI** – Mouse automation
- **pynput** – Input control

<<<<<<< HEAD
Use model_complexity: 0

🔮 Planned Features
Double click

Screenshot capture

Drag & drop

Zoom in / out

Previous slide gesture

Multi-hand support

📜 License
This project is licensed under the MIT License.

🙌 Acknowledgments
MediaPipe – Hand tracking

OpenCV – Computer vision

PyAutoGUI – Mouse automation

pynput – Input control
=======
---
>>>>>>> 07fe34f (Finalize README updates)

Built with ❤️ to redefine touchless human–computer interaction.