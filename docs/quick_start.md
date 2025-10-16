# Artisan-1 Quick Start Guide

Get your Artisan-1 robot up and running quickly!

---

## Prerequisites Checklist

- [ ] 3D printer with ≥200×200×200mm build volume
- [ ] All components from [BOM](BOM.md) ordered and received
- [ ] Raspberry Pi 5 (8GB recommended)
- [ ] MicroSD card (64GB+ A2 class)
- [ ] Basic tools: screwdrivers, pliers, soldering iron
- [ ] Computer for SD card setup

---

## Step 1: 3D Printing (Start Early!)

### Print Settings
```
Material: PLA
Layer Height: 0.2mm
Infill: 30-40% for structural parts, 15% for cosmetic
Perimeters: 3-4 walls for strength
Support: Yes (for overhangs >45°)
Build Plate Adhesion: Brim or raft recommended
```

### Print Queue (by priority)

**Phase 1 - Electronics Test Mount** (~10 hours)
- [ ] `torso_electronics_bay.stl`
- [ ] `servo_test_bracket.stl`

**Phase 2 - Hands & Arms** (~40 hours)
- [ ] `hand_left_palm.stl`
- [ ] `hand_left_fingers.stl`
- [ ] `hand_left_thumb.stl`
- [ ] `hand_right_*.stl` (mirror)
- [ ] `forearm_left.stl`
- [ ] `forearm_right.stl`
- [ ] `upper_arm_left.stl`
- [ ] `upper_arm_right.stl`
- [ ] `shoulder_assembly_*.stl`

**Phase 3 - Legs** (~60 hours)
- [ ] `foot_left.stl`
- [ ] `ankle_bracket_left.stl`
- [ ] `lower_leg_left.stl`
- [ ] `knee_joint_left.stl`
- [ ] `upper_leg_left.stl`
- [ ] `hip_assembly_left.stl`
- [ ] Right leg parts (mirror)

**Phase 4 - Torso & Head** (~40 hours)
- [ ] `torso_front.stl`
- [ ] `torso_back.stl`
- [ ] `head_base.stl`
- [ ] `head_pan_bracket.stl`
- [ ] `camera_mount.stl`

**Total Print Time: ~150 hours** (6-7 days continuous)

**Pro Tip:** Start printing while waiting for electronics to arrive!

---

## Step 2: Raspberry Pi Setup

### 2.1 Flash SD Card

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Select **Raspberry Pi OS (64-bit)** (Debian Bookworm based)
3. Configure:
   - Hostname: `artisan1`
   - Enable SSH
   - Set username/password
   - Configure WiFi (optional)
4. Flash to SD card

### 2.2 First Boot

```bash
# SSH into Pi
ssh pi@artisan1.local

# Update system
sudo apt update && sudo apt upgrade -y

# Enable I2C, SPI, Camera
sudo raspi-config
# Navigate to: Interface Options
# Enable: I2C, SPI, Camera
# Reboot when prompted
```

### 2.3 Install Dependencies

```bash
# Install system packages
sudo apt install -y python3-pip python3-opencv \
    libatlas-base-dev i2c-tools git

# Clone repository
cd ~
git clone https://github.com/KaiDream/Artisan-1.git
cd Artisan-1

# Install Python packages
pip3 install -r requirements.txt

# Verify I2C
sudo i2cdetect -y 1
# Should show empty bus (devices not connected yet)
```

---

## Step 3: Power System Assembly

**⚠️ CRITICAL: Do this before connecting any electronics!**

### 3.1 UBEC Setup

```
Battery (3S LiPo)
    │
    ├─→ 10A UBEC → 6V Rail (Servos)
    │
    └─→ 5A UBEC → 5V Rail (Logic)
```

### 3.2 Wiring

1. **Solder XT60 connector** to battery leads
2. **Connect UBECs:**
   - Red (battery +) → UBEC input (+)
   - Black (battery -) → UBEC input (-)
3. **Test voltages with multimeter:**
   - 10A UBEC output: 6.0V ±0.2V
   - 5A UBEC output: 5.0V ±0.1V
4. **Create distribution board:**
   - Servo rail: Multiple parallel XT60 connectors
   - Logic rail: USB-C cable to Pi

**⚠️ WARNING:** Never connect battery with reversed polarity!

---

## Step 4: Electronics Test Bench

### 4.1 Mount Electronics

Use `torso_electronics_bay.stl` to mount:
- Raspberry Pi 5
- 2× PCA9685 PWM boards
- ADS1115 ADC (optional for initial test)

### 4.2 Wire I2C Bus

```
Raspberry Pi 5:
  Pin 3 (SDA) ──┬─→ PCA9685 #1 SDA ──→ PCA9685 #2 SDA
  Pin 5 (SCL) ──┼─→ PCA9685 #1 SCL ──→ PCA9685 #2 SCL
  Pin 9 (GND) ──┴─→ Common GND
```

### 4.3 Test I2C

```bash
cd ~/Artisan-1
python3 tests/test_subsystems.py i2c

# Expected output:
# Found 2 I2C devices:
#   - 0x40 (PCA9685 #1)
#   - 0x41 (PCA9685 #2)
```

### 4.4 Test Single Servo

```bash
# Connect one PWM servo to PCA9685 board 1, channel 0
# Power: 6V rail, Signal: PCA9685 output

python3 -c "
from software.servo_controller import PWMServoController
import time

pwm = PWMServoController()
print('Moving servo...')
pwm.set_angle(1, 0, 0)    # 0 degrees
time.sleep(1)
pwm.set_angle(1, 0, 90)   # 90 degrees
time.sleep(1)
pwm.set_angle(1, 0, 180)  # 180 degrees
print('Done!')
"
```

**✓ Servo should sweep 0° → 90° → 180°**

---

## Step 5: Serial Servo Setup

### 5.1 Configure UART

Edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt

# Add these lines:
enable_uart=1
dtoverlay=disable-bt
```

Reboot:
```bash
sudo reboot
```

### 5.2 Wire Serial Bus

```
Raspberry Pi 5:
  Pin 8 (TX) → LX-16A Data (all servos daisy-chained)
  Pin 10 (RX) → LX-16A Data
  6V Rail → LX-16A VCC (all servos)
  GND → LX-16A GND (all servos)
```

### 5.3 Set Servo IDs

**IMPORTANT:** Each servo needs unique ID (1-10 for legs)

```bash
python3 -c "
from software.servo_controller import LX16AServoController

ctrl = LX16AServoController()

# Set servo ID (one servo connected at a time!)
ctrl._send_command(254, 13, bytes([1]))  # Set to ID 1
print('Servo ID set to 1')
"

# Disconnect, connect next servo, set to ID 2, etc.
```

### 5.4 Test Serial Servo

```bash
python3 tests/test_subsystems.py serial

# Expected: Position reading from servo ID 1
```

---

## Step 6: Camera Setup

```bash
# Test camera
libcamera-hello

# Should show camera preview for 5 seconds

# Test with Python
python3 tests/test_subsystems.py camera
```

---

## Step 7: Mechanical Assembly

### 7.1 Hand Assembly

1. Insert servos into `hand_*_palm.stl`
2. Attach finger linkages
3. Test grasp mechanism manually
4. Install FSR sensors on fingertips (if using tactile)

### 7.2 Arm Assembly

1. Install servos in shoulder, elbow, wrist
2. Connect servo horns to linkages
3. Test range of motion
4. Wire servos to PCA9685 channels (see config)

### 7.3 Leg Assembly

1. Install LX-16A servos in hip, knee, ankle
2. Wire in daisy-chain configuration
3. Label each servo with its ID (1-10)

### 7.4 Full Assembly

1. Attach arms to torso
2. Attach legs to torso
3. Mount head with camera
4. Route all wiring through torso
5. Secure electronics bay

---

## Step 8: Software Configuration

### 8.1 Servo Calibration

```bash
cd ~/Artisan-1/software

# Edit servo mapping if needed
nano ../config/robot_config.json

# Run calibration
python3 -c "
from servo_controller import ArtisanServoController
from servo_controller import JointLocation

ctrl = ArtisanServoController()

# Test each joint and record offsets
ctrl.set_joint_angle(JointLocation.LEFT_ELBOW, 90)
# Manually measure actual angle, calculate offset
"
```

Update offsets in `config/robot_config.json`

### 8.2 Camera Calibration

```bash
# Test vision system
python3 software/vision.py

# Adjust camera height/tilt in config if needed
```

### 8.3 Tactile Calibration

```bash
# With hands OPEN and unloaded
python3 software/tactile_sensing.py

# Follow on-screen prompts
```

---

## Step 9: Run First Demo!

```bash
cd ~/Artisan-1/software

# Run complete system test
python3 ../tests/test_subsystems.py

# If all tests pass, run demo
python3 main.py
```

### Demo Sequence

1. Robot calibrates sensors
2. Moves to neutral pose
3. Prompts: "Place fabric on table..."
4. Press Enter when ready
5. Robot scans for fabric corner
6. Reaches and grasps
7. Lifts fabric
8. Returns to neutral

**🎉 SUCCESS!**

---

## Troubleshooting

### Servos not responding
- Check 6V power rail voltage
- Verify I2C addresses: `sudo i2cdetect -y 1`
- Check servo wiring and polarity

### Camera not detected
- `sudo raspi-config` → Enable Camera
- Check ribbon cable connection
- Try: `libcamera-hello`

### Import errors
- Ensure virtual environment activated (if using)
- Reinstall: `pip3 install -r requirements.txt`

### Servo jitter
- Insufficient power → check UBEC capacity
- Poor wiring → shorten servo cables
- EMI → add capacitors to power rails

### IK solver fails
- Target out of reach → check coordinates
- Joint limits → see config file
- Verify arm geometry parameters

---

## Safety Checklist

- [ ] Emergency stop button accessible
- [ ] Robot secured during testing (can't fall)
- [ ] LiPo battery safety bag for charging
- [ ] No loose wires near moving parts
- [ ] Adequate ventilation for electronics
- [ ] Fuse on battery line (optional but recommended)

---

## Next Steps

1. **Tune IK parameters** for better accuracy
2. **Train custom vision model** for fabric detection
3. **Implement walking gait** using leg servos
4. **Add IMU** for balance control
5. **Join the community** and share your build!

---

## Getting Help

- **Issues:** https://github.com/KaiDream/Artisan-1/issues
- **Discussions:** https://github.com/KaiDream/Artisan-1/discussions
- **Email:** kaidream78@gmail.com

---

**Build time estimate: 40-60 hours**  
**Difficulty: Advanced (suitable for experienced makers)**

Good luck with your build! 🤖
