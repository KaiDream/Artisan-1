# Artisan-1 Software Architecture

Comprehensive overview of the software stack for the Artisan-1 humanoid robot.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              Main Control System                     │
│                  (main.py)                          │
│                                                      │
│  ┌──────────────────────────────────────────┐      │
│  │     Robot State Machine                   │      │
│  │  IDLE → SCANNING → REACHING → GRASPING   │      │
│  └──────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘
           │          │          │          │
    ┌──────┴───┐  ┌──┴───┐  ┌───┴────┐  ┌─┴──────┐
    │  Servo   │  │Vision│  │Tactile │  │ Kine-  │
    │Controller│  │System│  │Sensing │  │matics  │
    └──────────┘  └──────┘  └────────┘  └────────┘
```

---

## Module Descriptions

### 1. `main.py` - Main Control System

**Purpose:** Orchestrates all subsystems and implements high-level behaviors.

**Key Classes:**
- `RobotState` - Enumeration of robot operational states
- `Artisan1Robot` - Main robot controller

**State Machine:**
```
INITIALIZING → IDLE ↔ CALIBRATING
                 ↓
              SCANNING → REACHING → GRASPING → LIFTING
                 ↓          ↓          ↓
              ERROR ← ─ ─ ─ ─ ─ ─ ─ ─ ─
                 ↓
              SHUTDOWN
```

**Key Methods:**
- `calibrate_sensors()` - Calibrate tactile sensors
- `move_to_neutral_pose()` - Home position
- `fabric_corner_grasp_demo()` - Main demonstration
- `emergency_stop()` - Safety shutdown

**Lines of Code:** 312

---

### 2. `servo_controller.py` - Hybrid Servo Control

**Purpose:** Unified interface for PWM and serial bus servos.

**Key Classes:**

#### `PWMServoController`
Controls 16 PWM servos via 2x PCA9685 boards over I2C.

**Methods:**
- `set_angle(board, channel, angle)` - Position control
- `set_pulse_width(board, channel, pulse_us)` - Direct PWM control

#### `LX16AServoController`
Controls 10 LX-16A serial servos via UART.

**Methods:**
- `move_servo(id, position, time_ms)` - Timed movement
- `read_position(id)` - Position feedback
- `read_temperature(id)` - Thermal monitoring
- `read_voltage(id)` - Power monitoring

#### `ArtisanServoController`
High-level unified interface.

**Methods:**
- `set_joint_angle(joint, angle, time_ms)` - Named joint control
- `read_joint_position(joint)` - Feedback from serial servos
- `get_leg_positions()` - All leg joint positions
- `emergency_stop()` - Halt all servos

**Communication Protocols:**
- I2C for PCA9685 (address 0x40, 0x41)
- UART for LX-16A (115200 baud, /dev/ttyAMA0)

**Lines of Code:** 426

---

### 3. `tactile_sensing.py` - Force Sensing

**Purpose:** DIY tactile sensing using FSR arrays.

**Key Classes:**

#### `FSRSensor`
Individual force-sensitive resistor.

**Circuit:**
```
VCC (5V) → FSR → ADC_PIN + 10kΩ → GND
```

**Methods:**
- `calibrate_baseline()` - Zero calibration
- `read()` - Get FSRReading with force estimate
- `is_pressed(threshold)` - Binary touch detection

#### `TactileSensorArray`
Array of 4 FSR sensors via ADS1115 ADC.

**Methods:**
- `add_sensor(channel, id)` - Configure sensor
- `calibrate_all()` - Calibrate all sensors
- `read_all()` - Get all readings
- `check_grasp(required_sensors, threshold)` - Grasp validation
- `get_grasp_force()` - Total force calculation

#### `ArtisanHandSensing`
Dual-hand tactile system.

**Configuration:**
- Left hand: ADS1115 @ 0x48
- Right hand: ADS1115 @ 0x49 (optional)

**Methods:**
- `check_left_grasp()` - Left hand grasp confirmation
- `check_right_grasp()` - Right hand grasp confirmation
- `get_all_readings()` - Complete sensor state

**Lines of Code:** 329

---

### 4. `vision.py` - Computer Vision

**Purpose:** AI-powered object detection and fabric recognition.

**Key Classes:**

#### `VisionSystem`
TensorFlow Lite vision pipeline.

**Configuration:**
- Camera: Pi Camera Module 3
- Resolution: 640x480 (configurable)
- Model: MobileNetV2-SSD (COCO dataset)
- Inference: TensorFlow Lite

**Methods:**
- `capture_frame()` - Grab RGB image
- `detect_objects(image)` - Run object detection
- `draw_detections(image, detections)` - Visualize results
- `find_fabric_corner(image)` - Edge detection for fabric
- `pixel_to_3d(pixel_coords)` - Camera projection

**Performance:**
- Inference time: ~100-200ms per frame on Pi 5
- FPS: 5-10 with visualization

#### `FabricDetector`
Specialized fabric corner detection.

**Methods:**
- `detect_and_localize()` - Find fabric and return 3D coords

**Detection Pipeline:**
1. Capture frame
2. Convert to grayscale
3. Gaussian blur
4. Canny edge detection
5. Contour detection
6. Approximate polygon
7. Extract corner point
8. Project to 3D coordinates

**Lines of Code:** 398

---

### 5. `kinematics.py` - Inverse Kinematics

**Purpose:** 5-DOF arm control with IK solver.

**Key Classes:**

#### `ArmConfiguration`
Kinematic parameters and joint limits.

**Parameters:**
```python
shoulder_offset: 0.05 m
upper_arm_length: 0.25 m
forearm_length: 0.20 m
hand_length: 0.10 m
```

**Joint Limits:**
- Shoulder pitch: -90° to 180°
- Shoulder roll: -90° to 90°
- Shoulder yaw: -90° to 90°
- Elbow: 0° to 150°
- Wrist: -90° to 90°

#### `InverseKinematics`
Geometric IK solver.

**Methods:**
- `forward_kinematics(angles)` - FK for verification
- `solve_ik(x, y, z, arm_side)` - IK solution
- `solve_ik_with_orientation(x, y, z, angle)` - IK with end-effector orientation

**Algorithm:**
1. Calculate target distance and reachability
2. Solve shoulder yaw (horizontal plane)
3. Reduce to 2D problem in sagittal plane
4. Use law of cosines for elbow angle
5. Calculate shoulder angles
6. Verify joint limits

**Accuracy:** ~1-5mm error at typical reach distances

#### `ArmController`
High-level arm motion control.

**Methods:**
- `move_to_position(x, y, z, arm, time)` - Cartesian movement
- `reach_and_grasp(x, y, z, arm)` - Complete grasp sequence

**Grasp Sequence:**
1. Move to pre-grasp (5cm above target)
2. Open hand
3. Descend to target
4. Close grasp
5. Lift 10cm

**Lines of Code:** 397

---

## Data Flow

### Vision → Kinematics → Servo Control

```
Camera Capture (640x480 RGB)
    ↓
TFLite Inference (~150ms)
    ↓
Detected Objects (BBox + Confidence)
    ↓
Fabric Corner (pixel coordinates)
    ↓
3D Projection (world coordinates)
    ↓
IK Solver (joint angles)
    ↓
Servo Commands (PWM/Serial)
    ↓
Physical Movement
```

### Tactile Feedback Loop

```
FSR Voltage (ADC reading)
    ↓
Force Estimation (calibrated)
    ↓
Grasp Detection (threshold)
    ↓
State Machine Decision
    ↓
Action (retry/continue/success)
```

---

## Configuration System

### `config/robot_config.json`

**Sections:**
- `servo_configuration` - Hardware addresses
- `servo_mapping` - Joint-to-hardware mapping
- `vision_config` - Camera and model settings
- `tactile_config` - Sensor configuration
- `kinematics_config` - Arm geometry
- `power_config` - Battery specifications

**Usage:**
```python
import json

with open('config/robot_config.json') as f:
    config = json.load(f)

camera_res = config['vision_config']['camera_resolution']
```

---

## Dependencies

### Hardware Libraries
```
adafruit-circuitpython-pca9685  # PWM servo control
adafruit-circuitpython-ads1x15  # ADC for tactile
pyserial                         # LX-16A communication
picamera2                        # Camera interface
```

### Vision & AI
```
opencv-python                    # Image processing
tflite-runtime                   # TensorFlow Lite
numpy                           # Numerical operations
```

### Utilities
```
python-dotenv                   # Environment config
pyyaml                          # YAML parsing
```

---

## Error Handling

### Hierarchical Error Strategy

1. **Hardware Errors** - Try to recover, log, continue if possible
2. **Safety Violations** - Immediate emergency stop
3. **Unreachable Targets** - Graceful failure, user notification
4. **Sensor Failures** - Degrade gracefully, use defaults

### Logging Levels

```python
logging.DEBUG    # Detailed servo commands, sensor readings
logging.INFO     # State transitions, task progress
logging.WARNING  # Recoverable errors, degraded mode
logging.ERROR    # Failed operations, safety issues
logging.CRITICAL # System shutdown required
```

**Log File:** `artisan1.log`

---

## Performance Metrics

| Subsystem | Latency | Throughput |
|-----------|---------|------------|
| Servo Command (PWM) | <1ms | 50 Hz |
| Servo Command (Serial) | ~2ms | 100 Hz |
| Tactile Reading | ~10ms | 100 Hz |
| Vision Inference | ~150ms | 6-7 FPS |
| IK Calculation | <1ms | 1000 Hz |
| Main Control Loop | ~50ms | 20 Hz |

---

## Testing Framework

### Unit Tests
- Individual servo control
- Sensor reading accuracy
- IK solver correctness

### Integration Tests
- Vision → IK pipeline
- Grasp → Tactile confirmation
- Power system stability

### System Tests
- Complete demonstration sequence
- Error recovery
- Long-duration operation

**Test Command:**
```bash
python tests/test_subsystems.py
```

---

## Future Enhancements

### Planned Features
- [ ] ROS2 integration for standard interfaces
- [ ] Web dashboard for monitoring and control
- [ ] Trajectory planning for smooth movements
- [ ] Machine learning for grasp prediction
- [ ] IMU integration for balance control

### Architecture Improvements
- [ ] Async servo control for parallelism
- [ ] Priority-based task scheduler
- [ ] Distributed processing (offload vision to PC)
- [ ] Plugin system for behaviors

---

*Last updated: October 2025*
