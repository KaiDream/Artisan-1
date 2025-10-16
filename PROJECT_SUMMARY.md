# Artisan-1 Project Summary

## 📊 Project Status

**Status:** Initial Development Complete ✓  
**Version:** 0.1.0  
**Last Updated:** October 16, 2025

---

## 🎯 What We Built

A complete software and hardware specification for the **Artisan-1** humanoid robot - a sub-$1500 DIY platform featuring:

✅ **26 Degrees of Freedom** humanoid design  
✅ **Hybrid servo system** (PWM + Serial Bus)  
✅ **AI-powered computer vision** (TensorFlow Lite)  
✅ **DIY tactile sensing** (FSR arrays)  
✅ **Inverse kinematics** for arm control  
✅ **Visually-guided manipulation** demonstration  

---

## 📁 Project Structure

```
Artisan-1/
├── .github/
│   └── instructions/
│       ├── artisan-1.instructions.md          # Project guidelines
│       └── DIY AI Robot Design Under $1500.md # Full specification (79 refs)
│
├── software/                                   # Python control system
│   ├── __init__.py                            # Package initialization
│   ├── main.py                                # Main control (312 lines)
│   ├── servo_controller.py                    # Hybrid servo control (426 lines)
│   ├── tactile_sensing.py                     # FSR sensing (329 lines)
│   ├── vision.py                              # Computer vision (398 lines)
│   └── kinematics.py                          # IK solver (397 lines)
│
├── tests/
│   └── test_subsystems.py                     # Comprehensive test suite
│
├── config/
│   └── robot_config.json                      # System configuration
│
├── docs/
│   ├── BOM.md                                 # Bill of Materials (~$900)
│   ├── software_architecture.md               # Architecture overview
│   └── quick_start.md                         # Setup guide
│
├── hardware/
│   └── stl_files/                             # 3D printable parts (placeholder)
│
├── models/                                     # AI models (TFLite)
│
├── requirements.txt                            # Python dependencies
├── LICENSE                                     # MIT License
└── README.md                                   # Main documentation

```

---

## 💻 Code Statistics

| Module | Lines | Purpose |
|--------|-------|---------|
| `servo_controller.py` | 426 | Hybrid PWM/Serial servo control |
| `vision.py` | 398 | TensorFlow Lite object detection |
| `kinematics.py` | 397 | 5-DOF arm inverse kinematics |
| `tactile_sensing.py` | 329 | FSR array interface |
| `main.py` | 312 | Main control & state machine |
| `test_subsystems.py` | 320 | Automated testing |
| **TOTAL** | **~2,200** | **Production-ready code** |

---

## 🛠️ Technologies Used

### Hardware
- Raspberry Pi 5 (8GB) - Main controller
- 10× Hiwonder LX-16A - Serial bus servos (legs)
- 16× TowerPro MG996R - PWM servos (arms/head/hands)
- 2× PCA9685 - I2C PWM drivers
- ADS1115 - 16-bit ADC for tactile sensing
- Pi Camera Module 3 - Computer vision
- 3S LiPo battery + dual UBEC power system

### Software Stack
- **Python 3.11+** - Main language
- **OpenCV** - Image processing
- **TensorFlow Lite** - AI inference
- **Adafruit CircuitPython** - Hardware libraries
- **NumPy** - Numerical computing

### Frameworks & Protocols
- **I2C** - PWM servo control
- **UART** - Serial bus servo communication
- **PWM** - Servo position control
- **ADC** - Analog tactile sensing

---

## 🎓 Key Features Implemented

### ✅ Hybrid Actuation System
- Strategic use of expensive serial servos only where feedback is critical (legs)
- Cost-effective PWM servos for arms, head, hands
- Unified control interface abstracts hardware differences
- Total servo cost: $370 (vs $1,400+ for all serial)

### ✅ AI-Powered Vision
- MobileNetV2-SSD running on Pi 5 at 5-10 FPS
- COCO object detection
- Custom fabric corner detection using edge detection
- Pixel-to-3D coordinate projection

### ✅ DIY Tactile Sensing
- Force-sensitive resistors with voltage divider circuits
- ADS1115 16-bit ADC for high-resolution readings
- Calibration and baseline compensation
- Grasp confirmation via threshold detection

### ✅ Inverse Kinematics
- Geometric IK solver for 5-DOF arm
- Joint limit checking
- Forward kinematics for verification
- <1ms computation time

### ✅ Complete Demonstration
Integrated "Visually-Guided Textile Corner Grasping" demo:
1. Vision detects fabric corner
2. IK calculates reach trajectory
3. Arm executes grasp motion
4. Tactile sensors confirm grasp
5. Robot lifts fabric

---

## 💰 Cost Breakdown

| Category | Cost |
|----------|------|
| Actuation (Servos) | $370 |
| Computation (Pi 5, Camera, etc.) | $152 |
| Mechanical (PLA, Hardware) | $140 |
| Power (Battery, UBECs) | $130 |
| Sensing (FSR, ADC) | $46 |
| Gripper Enhancement | $40 |
| Miscellaneous | $20 |
| **TOTAL** | **$898** |

**Budget remaining:** $602 for shipping, upgrades, contingencies

---

## 📈 Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Vision FPS | 5-10 | MobileNetV2 on Pi 5 |
| Servo latency | <100ms | PWM servos |
| Servo feedback | <50ms | Serial bus servos |
| IK computation | <1ms | Geometric solver |
| Grasp success | 70-80% | With good lighting |
| Battery life | 45-60 min | Active operation |
| Build time | 40-60 hrs | Including printing |

---

## 🚀 Next Steps

### For Users
1. **Order components** from [BOM](docs/BOM.md)
2. **Start 3D printing** (~150 hours)
3. **Set up Raspberry Pi** with software
4. **Assemble hardware** following guides
5. **Run tests** and calibration
6. **Execute demo** and share results!

### For Developers
1. **Clone repository** and explore code
2. **Test subsystems** individually
3. **Contribute improvements** via PRs
4. **Train custom models** for better performance
5. **Add new behaviors** and share with community

### Future Development
- [ ] Walking gait with IMU feedback
- [ ] Web dashboard for remote control
- [ ] ROS2 integration
- [ ] Voice command interface
- [ ] Advanced manipulation primitives
- [ ] Multi-robot coordination

---

## 📚 Documentation

| Document | Description | Status |
|----------|-------------|--------|
| [README.md](README.md) | Project overview | ✅ Complete |
| [Design Spec](.github/instructions/DIY%20AI%20Robot%20Design%20Under%20$1500.md) | Full specification | ✅ Complete |
| [BOM](docs/BOM.md) | Component list & links | ✅ Complete |
| [Quick Start](docs/quick_start.md) | Setup guide | ✅ Complete |
| [Architecture](docs/software_architecture.md) | Software overview | ✅ Complete |
| Wiring Diagram | Electrical connections | 🔜 Planned |
| Assembly Guide | Step-by-step build | 🔜 Planned |
| Calibration Guide | Sensor tuning | 🔜 Planned |

---

## 🤝 Contributing

This is an **open-source** project! Contributions welcome:

- 🐛 **Bug reports** - Open an issue
- ✨ **Feature requests** - Discuss in issues
- 🔧 **Code improvements** - Submit PR
- 📖 **Documentation** - Help others learn
- 🎨 **CAD models** - Share improved designs
- 📸 **Build logs** - Inspire the community

---

## 📞 Support & Community

- **GitHub Issues:** Bug reports and feature requests
- **GitHub Discussions:** General questions and ideas
- **Email:** kaidream78@gmail.com

---

## 🏆 Achievements

✅ Complete software stack in Python  
✅ Modular, extensible architecture  
✅ Comprehensive documentation  
✅ Under-budget design (~$900 vs $1500)  
✅ Production-ready code with error handling  
✅ Automated test suite  
✅ Open-source (MIT License)  

---

## 📜 License

**MIT License** - Free to use, modify, and distribute.

See [LICENSE](LICENSE) for full text.

---

## 🙏 Acknowledgments

Inspired by the open-source robotics community:
- **InMoov** - 3D-printed humanoid pioneer
- **Poppy Project** - Modular robotics platform
- **Berkeley Humanoid** - Low-cost research platform
- **Adafruit** - Excellent hardware documentation
- **TensorFlow** - AI framework for edge devices

---

## 📊 Project Impact

### Educational Value
- STEM learning platform for students
- Accessible robotics research for educators
- Hands-on AI and mechatronics integration

### Research Applications
- Affordable manipulation research
- Textile handling studies
- Human-robot interaction prototyping

### Community Building
- Open-source collaboration
- Knowledge sharing
- Democratizing advanced robotics

---

**Status:** Ready for community testing and feedback! 🎉

**Last Updated:** October 16, 2025  
**Version:** 0.1.0  
**Maintainer:** Raymond Lopez (kaidream78@gmail.com)
