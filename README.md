# Artisan-1 Humanoid Robot

![Artisan-1 Logo](docs/images/artisan-1-header.png)

**A Sub-$1500 DIY Humanoid AI Robot with Tactile and Textile Manipulation Capabilities**

Design by Raymond Lopez ([kaidream78@gmail.com](mailto:kaidream78@gmail.com))

---

## 🤖 Project Overview

Artisan-1 is an open-source, 3D-printable humanoid robot designed to be built at home for under $1500. It features:

- **26 Degrees of Freedom** - Full humanoid articulation
- **Hybrid Actuation System** - Strategic mix of PWM and serial bus servos
- **AI-Powered Vision** - TensorFlow Lite object detection on Raspberry Pi 5
- **Tactile Sensing** - DIY FSR arrays for grasp confirmation
- **Advanced Manipulation** - Visually-guided textile corner grasping

This project demonstrates that sophisticated robotics research capabilities are accessible to home builders and educators without requiring academic-level budgets.

---

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Bill of Materials](#bill-of-materials)
- [Getting Started](#getting-started)
- [Software Setup](#software-setup)
- [Documentation](#documentation)
- [Contributing](#contributing)

---

## ✨ Features

### Mechanical
- **80-100cm tall** bipedal humanoid
- **Fully 3D printable** with PLA filament (4-5kg required)
- **Modular design** inspired by InMoov and Poppy Project
- **High-friction grippers** with silicone overmolding

### Actuation
- **10x Hiwonder LX-16A** serial bus servos for legs (position feedback)
- **16x TowerPro MG996R** PWM servos for arms, head, hands
- **Underactuated hands** for simplified yet effective grasping

### Computation
- **Raspberry Pi 5 (8GB)** - Main brain for AI and control
- **2x PCA9685** - 16-channel PWM drivers for servo control
- **ADS1115** - 16-bit ADC for tactile sensing

### AI & Software
- **TensorFlow Lite** - Real-time object detection
- **MobileNetV2-SSD** - Optimized for edge devices
- **OpenCV** - Image processing and computer vision
- **Custom IK solver** - Inverse kinematics for arm control

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Raspberry Pi 5                        │
│                   (Main Controller)                      │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐           │
│  │ Vision   │  │ Tactile  │  │ Kinematics │           │
│  │ AI (TF)  │  │ Sensing  │  │ IK Solver  │           │
│  └──────────┘  └──────────┘  └────────────┘           │
└─────────────────────────────────────────────────────────┘
```

See [full architecture diagram](docs/architecture.md).

---

## 💰 Bill of Materials

Estimated total: **~$900** (well under $1500 budget)

Key components:
- 10x Hiwonder LX-16A Serial Servos: $210
- 16x TowerPro MG996R PWM Servos: $160
- Raspberry Pi 5 (8GB): $80
- 5kg PLA Filament: $100
- Power system (LiPo + UBECs): $105
- Sensors & electronics: $80

See [docs/BOM.md](docs/BOM.md) for complete list with supplier links.

---

## 🚀 Getting Started

### Quick Start

1. **Clone repository**
   ```bash
   git clone https://github.com/KaiDream/Artisan-1.git
   cd Artisan-1
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run tests**
   ```bash
   # Test individual subsystems
   python software/servo_controller.py
   python software/tactile_sensing.py
   python software/vision.py
   python software/kinematics.py
   ```

4. **Run main demo**
   ```bash
   python software/main.py
   ```

---

## 💻 Software Setup

### Raspberry Pi Configuration

```bash
# Enable I2C and Camera
sudo raspi-config

# Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-opencv libatlas-base-dev

# Install Python packages
pip install -r requirements.txt
```

### Software Modules

- **`servo_controller.py`** - Hybrid PWM/Serial servo control (426 lines)
- **`tactile_sensing.py`** - FSR array interface with ADS1115 (329 lines)
- **`vision.py`** - Computer vision with TensorFlow Lite (398 lines)
- **`kinematics.py`** - Inverse kinematics solver (397 lines)
- **`main.py`** - Main control loop and demonstration (312 lines)

---

## 📖 Documentation

- [Design Document](.github/instructions/DIY%20AI%20Robot%20Design%20Under%20$1500.md) - Complete specification
- [Bill of Materials](docs/BOM.md) - Detailed component list
- [Configuration](config/robot_config.json) - System configuration

---

## 🎯 Performance Metrics

- **Vision inference:** ~5-10 FPS with MobileNetV2-SSD
- **Servo response:** <100ms PWM, <50ms serial bus  
- **Battery runtime:** ~45-60 minutes active operation
- **Build time:** ~40-60 hours (printing + assembly)

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Walking gait implementation with IMU
- [ ] Custom fabric corner detection model
- [ ] Web-based control interface
- [ ] ROS2 integration

---

## 📧 Contact

**Raymond Lopez**  
Email: [kaidream78@gmail.com](mailto:kaidream78@gmail.com)  
GitHub: [@KaiDream](https://github.com/KaiDream)

---

**Built with ❤️ for the robotics community**
