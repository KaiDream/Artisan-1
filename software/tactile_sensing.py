"""
Tactile Sensing Module

Implements FSR (Force Sensitive Resistor) arrays with ADS1115 ADC
for tactile feedback in robot hands.
"""

import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
except ImportError:
    print("Warning: Adafruit ADS1x15 library not installed. Run: pip install adafruit-circuitpython-ads1x15")


logger = logging.getLogger(__name__)


@dataclass
class FSRReading:
    """Force Sensitive Resistor reading data"""
    sensor_id: str
    raw_value: int
    voltage: float
    force_estimate: float
    timestamp: float


class FSRSensor:
    """
    Individual Force Sensitive Resistor with voltage divider circuit.
    
    Circuit:
    VCC (5V) -> FSR -> ADC_PIN + 10kΩ Resistor -> GND
    
    As pressure increases, FSR resistance decreases, voltage at ADC pin increases.
    """
    
    def __init__(self, analog_channel: AnalogIn, sensor_id: str, 
                 pulldown_resistance: float = 10000.0):
        """
        Initialize FSR sensor.
        
        Args:
            analog_channel: ADS1115 analog input channel
            sensor_id: Unique identifier for this sensor
            pulldown_resistance: Fixed resistor value in ohms (default 10kΩ)
        """
        self.channel = analog_channel
        self.sensor_id = sensor_id
        self.pulldown_resistance = pulldown_resistance
        self.baseline_reading = 0
        self.calibrated = False
    
    def calibrate_baseline(self, num_samples: int = 10) -> None:
        """
        Calibrate baseline reading (no pressure).
        
        Args:
            num_samples: Number of samples to average
        """
        readings = []
        for _ in range(num_samples):
            readings.append(self.channel.value)
            time.sleep(0.01)
        
        self.baseline_reading = sum(readings) / len(readings)
        self.calibrated = True
        logger.info(f"{self.sensor_id} calibrated. Baseline: {self.baseline_reading}")
    
    def read(self) -> FSRReading:
        """
        Read current sensor value.
        
        Returns:
            FSRReading object with raw value, voltage, and force estimate
        """
        raw_value = self.channel.value
        voltage = self.channel.voltage
        
        # Estimate force based on voltage change from baseline
        # This is a simplified model - actual force requires calibration curve
        if self.calibrated:
            voltage_change = voltage - (self.baseline_reading * 5.0 / 32768)
            # Rough estimate: map voltage change to 0-100 force units
            force_estimate = max(0, min(100, voltage_change * 20))
        else:
            force_estimate = 0
        
        return FSRReading(
            sensor_id=self.sensor_id,
            raw_value=raw_value,
            voltage=voltage,
            force_estimate=force_estimate,
            timestamp=time.time()
        )
    
    def is_pressed(self, threshold: float = 0.5) -> bool:
        """
        Check if sensor detects pressure above threshold.
        
        Args:
            threshold: Voltage threshold in volts
            
        Returns:
            True if pressed, False otherwise
        """
        return self.channel.voltage > threshold


class TactileSensorArray:
    """
    Array of FSR sensors for robot hand tactile sensing.
    Uses ADS1115 16-bit ADC to read up to 4 FSR sensors.
    """
    
    def __init__(self, i2c_address: int = 0x48):
        """
        Initialize tactile sensor array with ADS1115.
        
        Args:
            i2c_address: I2C address of ADS1115 (default 0x48)
        """
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS.ADS1115(i2c, address=i2c_address)
            
            # Create analog input channels
            self.channels = {
                0: AnalogIn(self.ads, ADS.P0),
                1: AnalogIn(self.ads, ADS.P1),
                2: AnalogIn(self.ads, ADS.P2),
                3: AnalogIn(self.ads, ADS.P3)
            }
            
            self.sensors: Dict[str, FSRSensor] = {}
            logger.info(f"ADS1115 initialized at address 0x{i2c_address:02X}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ADS1115: {e}")
            raise
    
    def add_sensor(self, channel: int, sensor_id: str) -> None:
        """
        Add FSR sensor to array.
        
        Args:
            channel: ADC channel (0-3)
            sensor_id: Unique identifier (e.g., "left_index", "right_thumb")
        """
        if channel not in self.channels:
            raise ValueError(f"Invalid channel: {channel}. Must be 0-3")
        
        self.sensors[sensor_id] = FSRSensor(self.channels[channel], sensor_id)
        logger.info(f"Added sensor '{sensor_id}' on channel {channel}")
    
    def calibrate_all(self) -> None:
        """Calibrate all sensors in array"""
        logger.info("Calibrating all sensors...")
        for sensor_id, sensor in self.sensors.items():
            sensor.calibrate_baseline()
    
    def read_sensor(self, sensor_id: str) -> Optional[FSRReading]:
        """
        Read specific sensor.
        
        Args:
            sensor_id: Sensor identifier
            
        Returns:
            FSRReading or None if sensor not found
        """
        if sensor_id in self.sensors:
            return self.sensors[sensor_id].read()
        logger.warning(f"Sensor '{sensor_id}' not found")
        return None
    
    def read_all(self) -> Dict[str, FSRReading]:
        """
        Read all sensors in array.
        
        Returns:
            Dictionary of sensor readings
        """
        readings = {}
        for sensor_id, sensor in self.sensors.items():
            readings[sensor_id] = sensor.read()
        return readings
    
    def check_grasp(self, required_sensors: List[str], 
                    threshold: float = 0.5) -> bool:
        """
        Check if grasp is successful based on sensor activation.
        
        Args:
            required_sensors: List of sensor IDs that should detect pressure
            threshold: Voltage threshold for detection
            
        Returns:
            True if all required sensors detect pressure
        """
        for sensor_id in required_sensors:
            if sensor_id not in self.sensors:
                logger.warning(f"Required sensor '{sensor_id}' not found")
                return False
            
            if not self.sensors[sensor_id].is_pressed(threshold):
                return False
        
        return True
    
    def get_grasp_force(self, sensor_ids: Optional[List[str]] = None) -> float:
        """
        Calculate total grasp force from specified sensors.
        
        Args:
            sensor_ids: List of sensor IDs to include (None = all sensors)
            
        Returns:
            Total force estimate
        """
        if sensor_ids is None:
            sensor_ids = list(self.sensors.keys())
        
        total_force = 0.0
        for sensor_id in sensor_ids:
            if sensor_id in self.sensors:
                reading = self.sensors[sensor_id].read()
                total_force += reading.force_estimate
        
        return total_force


class ArtisanHandSensing:
    """
    High-level tactile sensing for Artisan-1 hands.
    Manages FSR arrays for both left and right hands.
    """
    
    def __init__(self):
        """Initialize tactile sensing for both hands"""
        # Left hand sensors (ADS1115 at 0x48)
        self.left_hand = TactileSensorArray(i2c_address=0x48)
        self.left_hand.add_sensor(0, "left_index")
        self.left_hand.add_sensor(1, "left_middle")
        self.left_hand.add_sensor(2, "left_ring")
        self.left_hand.add_sensor(3, "left_thumb")
        
        # Right hand sensors (ADS1115 at 0x49)
        # Note: Second ADS1115 requires address pin configuration
        try:
            self.right_hand = TactileSensorArray(i2c_address=0x49)
            self.right_hand.add_sensor(0, "right_index")
            self.right_hand.add_sensor(1, "right_middle")
            self.right_hand.add_sensor(2, "right_ring")
            self.right_hand.add_sensor(3, "right_thumb")
            self.dual_hand = True
        except Exception as e:
            logger.warning(f"Right hand ADC not available: {e}")
            self.right_hand = None
            self.dual_hand = False
        
        logger.info("Artisan Hand Sensing initialized")
    
    def calibrate(self) -> None:
        """Calibrate both hands (call when hands are open/unloaded)"""
        logger.info("Calibrating hand sensors. Ensure hands are open...")
        time.sleep(2)  # Give user time to ensure hands are clear
        
        self.left_hand.calibrate_all()
        if self.dual_hand and self.right_hand:
            self.right_hand.calibrate_all()
        
        logger.info("Calibration complete")
    
    def check_left_grasp(self, threshold: float = 0.5) -> bool:
        """
        Check if left hand has successful grasp.
        
        Args:
            threshold: Detection threshold in volts
            
        Returns:
            True if grasping object
        """
        # Require at least index and thumb to detect pressure
        return self.left_hand.check_grasp(
            ["left_index", "left_thumb"], 
            threshold
        )
    
    def check_right_grasp(self, threshold: float = 0.5) -> bool:
        """
        Check if right hand has successful grasp.
        
        Args:
            threshold: Detection threshold in volts
            
        Returns:
            True if grasping object
        """
        if not self.dual_hand or not self.right_hand:
            logger.warning("Right hand sensors not available")
            return False
        
        return self.right_hand.check_grasp(
            ["right_index", "right_thumb"], 
            threshold
        )
    
    def get_all_readings(self) -> Dict[str, Dict[str, FSRReading]]:
        """
        Get readings from all hand sensors.
        
        Returns:
            Dictionary with 'left' and 'right' hand readings
        """
        readings = {
            "left": self.left_hand.read_all()
        }
        
        if self.dual_hand and self.right_hand:
            readings["right"] = self.right_hand.read_all()
        
        return readings
    
    def print_status(self) -> None:
        """Print current status of all sensors"""
        all_readings = self.get_all_readings()
        
        print("\n=== Tactile Sensor Status ===")
        for hand_name, hand_readings in all_readings.items():
            print(f"\n{hand_name.upper()} HAND:")
            for sensor_id, reading in hand_readings.items():
                print(f"  {sensor_id:15s}: {reading.voltage:0.3f}V  "
                      f"Force: {reading.force_estimate:5.1f}")


if __name__ == "__main__":
    # Test script
    logging.basicConfig(level=logging.INFO)
    
    print("Initializing Artisan-1 Tactile Sensing...")
    try:
        hands = ArtisanHandSensing()
        
        print("\nCalibrating sensors in 3 seconds...")
        print("Make sure hands are open and unloaded!")
        time.sleep(3)
        hands.calibrate()
        
        print("\nReading sensors for 10 seconds...")
        print("Try pressing the fingertips!\n")
        
        for i in range(20):
            hands.print_status()
            
            if hands.check_left_grasp():
                print("\n>>> LEFT HAND GRASP DETECTED! <<<")
            
            if hands.check_right_grasp():
                print("\n>>> RIGHT HAND GRASP DETECTED! <<<")
            
            time.sleep(0.5)
        
        print("\nTest complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
