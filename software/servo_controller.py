"""
Servo Controller Module

Manages both PWM servos (via PCA9685) and Serial Bus servos (LX-16A)
for the hybrid actuation system of Artisan-1.
"""

import time
import logging
from typing import Dict, Optional, Tuple
from enum import Enum

try:
    from adafruit_servokit import ServoKit
    from adafruit_pca9685 import PCA9685
    import board
    import busio
except ImportError:
    print("Warning: Adafruit libraries not installed. Run: pip install adafruit-circuitpython-pca9685 adafruit-circuitpython-servokit")

try:
    import serial
except ImportError:
    print("Warning: pyserial not installed. Run: pip install pyserial")


logger = logging.getLogger(__name__)


class ServoType(Enum):
    """Servo type classification"""
    PWM = "pwm"
    SERIAL_BUS = "serial_bus"


class JointLocation(Enum):
    """Robot joint locations for servo mapping"""
    # Legs (Serial Bus Servos - LX-16A)
    LEFT_HIP_PITCH = "left_hip_pitch"
    LEFT_HIP_ROLL = "left_hip_roll"
    LEFT_HIP_YAW = "left_hip_yaw"
    LEFT_KNEE = "left_knee"
    LEFT_ANKLE = "left_ankle"
    
    RIGHT_HIP_PITCH = "right_hip_pitch"
    RIGHT_HIP_ROLL = "right_hip_roll"
    RIGHT_HIP_YAW = "right_hip_yaw"
    RIGHT_KNEE = "right_knee"
    RIGHT_ANKLE = "right_ankle"
    
    # Arms (PWM Servos - MG996R)
    LEFT_SHOULDER_PITCH = "left_shoulder_pitch"
    LEFT_SHOULDER_ROLL = "left_shoulder_roll"
    LEFT_SHOULDER_YAW = "left_shoulder_yaw"
    LEFT_ELBOW = "left_elbow"
    LEFT_WRIST = "left_wrist"
    
    RIGHT_SHOULDER_PITCH = "right_shoulder_pitch"
    RIGHT_SHOULDER_ROLL = "right_shoulder_roll"
    RIGHT_SHOULDER_YAW = "right_shoulder_yaw"
    RIGHT_ELBOW = "right_elbow"
    RIGHT_WRIST = "right_wrist"
    
    # Head (PWM Servos - MG996R)
    HEAD_PAN = "head_pan"
    HEAD_TILT = "head_tilt"
    
    # Hands (PWM Servos - MG996R)
    LEFT_HAND_FINGERS = "left_hand_fingers"
    LEFT_HAND_THUMB = "left_hand_thumb"
    RIGHT_HAND_FINGERS = "right_hand_fingers"
    RIGHT_HAND_THUMB = "right_hand_thumb"


class PWMServoController:
    """
    Controls standard PWM servos using PCA9685 driver boards.
    Manages 16 servos for arms, head, and hands.
    """
    
    def __init__(self, i2c_address_1: int = 0x40, i2c_address_2: int = 0x41):
        """
        Initialize two PCA9685 boards for 16 PWM servos.
        
        Args:
            i2c_address_1: I2C address of first PCA9685 board
            i2c_address_2: I2C address of second PCA9685 board
        """
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.kit_1 = ServoKit(channels=16, address=i2c_address_1)
            self.kit_2 = ServoKit(channels=16, address=i2c_address_2)
            logger.info("PWM Servo Controllers initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PWM controllers: {e}")
            raise
    
    def set_angle(self, board: int, channel: int, angle: float) -> None:
        """
        Set servo to specific angle.
        
        Args:
            board: Board number (1 or 2)
            channel: Channel on board (0-15)
            angle: Target angle in degrees (0-180)
        """
        try:
            if board == 1:
                self.kit_1.servo[channel].angle = angle
            elif board == 2:
                self.kit_2.servo[channel].angle = angle
            else:
                raise ValueError("Board must be 1 or 2")
        except Exception as e:
            logger.error(f"Error setting PWM servo angle: {e}")
    
    def set_pulse_width(self, board: int, channel: int, pulse_us: int) -> None:
        """
        Set servo pulse width directly in microseconds.
        
        Args:
            board: Board number (1 or 2)
            channel: Channel on board (0-15)
            pulse_us: Pulse width in microseconds (500-2500)
        """
        try:
            if board == 1:
                self.kit_1.servo[channel].set_pulse_width_range(pulse_us, pulse_us)
            elif board == 2:
                self.kit_2.servo[channel].set_pulse_width_range(pulse_us, pulse_us)
        except Exception as e:
            logger.error(f"Error setting PWM pulse width: {e}")


class LX16AServoController:
    """
    Controls LewanSoul/Hiwonder LX-16A serial bus servos.
    Manages 10 servos for the leg joints with position feedback.
    """
    
    # LX-16A Command definitions
    CMD_SERVO_MOVE_TIME_WRITE = 1
    CMD_SERVO_MOVE_TIME_READ = 2
    CMD_SERVO_MOVE_TIME_WAIT_WRITE = 7
    CMD_SERVO_MOVE_TIME_WAIT_READ = 8
    CMD_SERVO_MOVE_START = 11
    CMD_SERVO_MOVE_STOP = 12
    CMD_SERVO_ID_WRITE = 13
    CMD_SERVO_ID_READ = 14
    CMD_SERVO_ANGLE_OFFSET_ADJUST = 17
    CMD_SERVO_ANGLE_OFFSET_WRITE = 18
    CMD_SERVO_ANGLE_OFFSET_READ = 19
    CMD_SERVO_ANGLE_LIMIT_WRITE = 20
    CMD_SERVO_ANGLE_LIMIT_READ = 21
    CMD_SERVO_VIN_LIMIT_WRITE = 22
    CMD_SERVO_VIN_LIMIT_READ = 23
    CMD_SERVO_TEMP_MAX_LIMIT_WRITE = 24
    CMD_SERVO_TEMP_MAX_LIMIT_READ = 25
    CMD_SERVO_TEMP_READ = 26
    CMD_SERVO_VIN_READ = 27
    CMD_SERVO_POS_READ = 28
    CMD_SERVO_OR_MOTOR_MODE_WRITE = 29
    CMD_SERVO_OR_MOTOR_MODE_READ = 30
    CMD_SERVO_LOAD_OR_UNLOAD_WRITE = 31
    CMD_SERVO_LOAD_OR_UNLOAD_READ = 32
    
    def __init__(self, port: str = '/dev/ttyAMA0', baudrate: int = 115200):
        """
        Initialize serial connection to LX-16A servo chain.
        
        Args:
            port: Serial port (default /dev/ttyAMA0 for Pi UART)
            baudrate: Communication speed (default 115200)
        """
        try:
            self.serial = serial.Serial(port, baudrate, timeout=1)
            logger.info(f"LX-16A Serial Bus initialized on {port}")
        except Exception as e:
            logger.error(f"Failed to initialize LX-16A controller: {e}")
            raise
    
    def _calculate_checksum(self, packet: bytes) -> int:
        """Calculate LX-16A checksum"""
        return (~sum(packet[2:])) & 0xFF
    
    def _send_command(self, servo_id: int, cmd: int, params: bytes = b'') -> None:
        """
        Send command to servo.
        
        Args:
            servo_id: Servo ID (0-253)
            cmd: Command byte
            params: Command parameters
        """
        length = len(params) + 3
        packet = bytes([0x55, 0x55, servo_id, length, cmd]) + params
        checksum = self._calculate_checksum(packet)
        packet += bytes([checksum])
        self.serial.write(packet)
    
    def move_servo(self, servo_id: int, position: int, time_ms: int = 1000) -> None:
        """
        Move servo to position over specified time.
        
        Args:
            servo_id: Servo ID (1-10 for legs)
            position: Target position (0-1000)
            time_ms: Movement duration in milliseconds
        """
        pos_low = position & 0xFF
        pos_high = (position >> 8) & 0xFF
        time_low = time_ms & 0xFF
        time_high = (time_ms >> 8) & 0xFF
        
        params = bytes([pos_low, pos_high, time_low, time_high])
        self._send_command(servo_id, self.CMD_SERVO_MOVE_TIME_WRITE, params)
    
    def read_position(self, servo_id: int) -> Optional[int]:
        """
        Read current position of servo.
        
        Args:
            servo_id: Servo ID
            
        Returns:
            Current position (0-1000) or None if read failed
        """
        self._send_command(servo_id, self.CMD_SERVO_POS_READ)
        time.sleep(0.01)  # Wait for response
        
        if self.serial.in_waiting >= 10:
            response = self.serial.read(10)
            if len(response) == 10 and response[0:2] == b'\x55\x55':
                position = response[5] | (response[6] << 8)
                return position
        return None
    
    def read_temperature(self, servo_id: int) -> Optional[int]:
        """
        Read servo temperature.
        
        Args:
            servo_id: Servo ID
            
        Returns:
            Temperature in Celsius or None if read failed
        """
        self._send_command(servo_id, self.CMD_SERVO_TEMP_READ)
        time.sleep(0.01)
        
        if self.serial.in_waiting >= 7:
            response = self.serial.read(7)
            if len(response) == 7 and response[0:2] == b'\x55\x55':
                return response[5]
        return None
    
    def read_voltage(self, servo_id: int) -> Optional[float]:
        """
        Read servo input voltage.
        
        Args:
            servo_id: Servo ID
            
        Returns:
            Voltage in millivolts or None if read failed
        """
        self._send_command(servo_id, self.CMD_SERVO_VIN_READ)
        time.sleep(0.01)
        
        if self.serial.in_waiting >= 8:
            response = self.serial.read(8)
            if len(response) == 8 and response[0:2] == b'\x55\x55':
                voltage = response[5] | (response[6] << 8)
                return voltage
        return None
    
    def close(self):
        """Close serial connection"""
        if hasattr(self, 'serial') and self.serial.is_open:
            self.serial.close()


class ArtisanServoController:
    """
    Unified servo controller for Artisan-1 hybrid actuation system.
    Manages both PWM and Serial Bus servos with high-level joint control.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize hybrid servo control system.
        
        Args:
            config_file: Path to JSON servo configuration file
        """
        self.pwm_controller = PWMServoController()
        self.serial_controller = LX16AServoController()
        
        # Servo mapping: joint -> (type, board/id, channel)
        self.servo_map: Dict[JointLocation, Tuple[ServoType, int, int]] = {}
        
        if config_file:
            self._load_config(config_file)
        else:
            self._init_default_mapping()
        
        logger.info("Artisan Servo Controller initialized")
    
    def _load_config(self, config_file: str):
        """
        Load servo configuration from JSON file.
        
        Args:
            config_file: Path to configuration file
        """
        import json
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Parse servo mappings from config
        # This is a placeholder - implement full config parsing
        logger.info(f"Configuration loaded from {config_file}")
        self._init_default_mapping()  # Fall back to defaults for now
    
    def _init_default_mapping(self):
        """Initialize default servo mapping"""
        # Legs - Serial Bus Servos (ID 1-10)
        leg_joints_serial = [
            (JointLocation.LEFT_HIP_PITCH, 1),
            (JointLocation.LEFT_HIP_ROLL, 2),
            (JointLocation.LEFT_HIP_YAW, 3),
            (JointLocation.LEFT_KNEE, 4),
            (JointLocation.LEFT_ANKLE, 5),
            (JointLocation.RIGHT_HIP_PITCH, 6),
            (JointLocation.RIGHT_HIP_ROLL, 7),
            (JointLocation.RIGHT_HIP_YAW, 8),
            (JointLocation.RIGHT_KNEE, 9),
            (JointLocation.RIGHT_ANKLE, 10),
        ]
        
        for joint, servo_id in leg_joints_serial:
            self.servo_map[joint] = (ServoType.SERIAL_BUS, servo_id, 0)
        
        # Arms, Head, Hands - PWM Servos (Board 1 & 2, Channels 0-15)
        pwm_mapping = [
            # Board 1 (Channels 0-15)
            (JointLocation.LEFT_SHOULDER_PITCH, 1, 0),
            (JointLocation.LEFT_SHOULDER_ROLL, 1, 1),
            (JointLocation.LEFT_SHOULDER_YAW, 1, 2),
            (JointLocation.LEFT_ELBOW, 1, 3),
            (JointLocation.LEFT_WRIST, 1, 4),
            (JointLocation.RIGHT_SHOULDER_PITCH, 1, 5),
            (JointLocation.RIGHT_SHOULDER_ROLL, 1, 6),
            (JointLocation.RIGHT_SHOULDER_YAW, 1, 7),
            (JointLocation.RIGHT_ELBOW, 1, 8),
            (JointLocation.RIGHT_WRIST, 1, 9),
            # Board 2 (Channels 0-5)
            (JointLocation.HEAD_PAN, 2, 0),
            (JointLocation.HEAD_TILT, 2, 1),
            (JointLocation.LEFT_HAND_FINGERS, 2, 2),
            (JointLocation.LEFT_HAND_THUMB, 2, 3),
            (JointLocation.RIGHT_HAND_FINGERS, 2, 4),
            (JointLocation.RIGHT_HAND_THUMB, 2, 5),
        ]
        
        for joint, board, channel in pwm_mapping:
            self.servo_map[joint] = (ServoType.PWM, board, channel)
    
    def set_joint_angle(self, joint: JointLocation, angle: float, time_ms: int = 500) -> None:
        """
        Set joint to specific angle.
        
        Args:
            joint: Joint location enum
            angle: Target angle in degrees
            time_ms: Movement time (only for serial servos)
        """
        if joint not in self.servo_map:
            logger.error(f"Joint {joint} not found in servo map")
            return
        
        servo_type, param1, param2 = self.servo_map[joint]
        
        if servo_type == ServoType.PWM:
            # PWM servo: param1=board, param2=channel
            self.pwm_controller.set_angle(param1, param2, angle)
        elif servo_type == ServoType.SERIAL_BUS:
            # Serial servo: param1=servo_id, convert angle to position (0-1000)
            position = int(angle * 1000 / 240)  # LX-16A: 0-240 degrees = 0-1000 position
            self.serial_controller.move_servo(param1, position, time_ms)
    
    def read_joint_position(self, joint: JointLocation) -> Optional[float]:
        """
        Read current joint position (only for serial servos with feedback).
        
        Args:
            joint: Joint location enum
            
        Returns:
            Current angle in degrees or None
        """
        if joint not in self.servo_map:
            return None
        
        servo_type, servo_id, _ = self.servo_map[joint]
        
        if servo_type == ServoType.SERIAL_BUS:
            position = self.serial_controller.read_position(servo_id)
            if position is not None:
                return position * 240 / 1000  # Convert position to degrees
        
        logger.warning(f"Position feedback not available for {joint}")
        return None
    
    def get_leg_positions(self) -> Dict[JointLocation, Optional[float]]:
        """
        Read all leg joint positions for balance/gait control.
        
        Returns:
            Dictionary of leg joint positions in degrees
        """
        leg_joints = [
            JointLocation.LEFT_HIP_PITCH, JointLocation.LEFT_HIP_ROLL,
            JointLocation.LEFT_HIP_YAW, JointLocation.LEFT_KNEE,
            JointLocation.LEFT_ANKLE, JointLocation.RIGHT_HIP_PITCH,
            JointLocation.RIGHT_HIP_ROLL, JointLocation.RIGHT_HIP_YAW,
            JointLocation.RIGHT_KNEE, JointLocation.RIGHT_ANKLE
        ]
        
        positions = {}
        for joint in leg_joints:
            positions[joint] = self.read_joint_position(joint)
        
        return positions
    
    def emergency_stop(self):
        """Stop all servos immediately"""
        logger.warning("EMERGENCY STOP ACTIVATED")
        # Send stop command to all serial servos
        for i in range(1, 11):
            try:
                self.serial_controller._send_command(i, LX16AServoController.CMD_SERVO_MOVE_STOP)
            except Exception as e:
                logger.error(f"Error stopping servo {i}: {e}")
    
    def shutdown(self):
        """Safely shutdown servo controllers"""
        logger.info("Shutting down servo controllers")
        self.serial_controller.close()


if __name__ == "__main__":
    # Test script
    logging.basicConfig(level=logging.INFO)
    
    print("Initializing Artisan-1 Servo Controller...")
    try:
        controller = ArtisanServoController()
        print("Controller initialized successfully!")
        
        # Example: Move head
        print("Moving head...")
        controller.set_joint_angle(JointLocation.HEAD_PAN, 90)
        time.sleep(1)
        controller.set_joint_angle(JointLocation.HEAD_TILT, 45)
        
        # Example: Read leg position
        print("Reading left knee position...")
        pos = controller.read_joint_position(JointLocation.LEFT_KNEE)
        print(f"Left knee position: {pos} degrees")
        
        controller.shutdown()
        
    except Exception as e:
        print(f"Error: {e}")
