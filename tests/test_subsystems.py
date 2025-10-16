"""
Test Suite for Artisan-1 Subsystems

Run individual tests or comprehensive system validation.
"""

import logging
import time
import sys
from typing import Dict, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResult:
    """Test result container"""
    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message


class Artisan1TestSuite:
    """Comprehensive test suite for all subsystems"""
    
    def __init__(self):
        self.results: Dict[str, TestResult] = {}
    
    def test_i2c_devices(self) -> TestResult:
        """Test I2C bus and detect connected devices"""
        logger.info("Testing I2C bus...")
        
        try:
            import board
            import busio
            
            i2c = busio.I2C(board.SCL, board.SDA)
            
            # Scan for devices
            while not i2c.try_lock():
                time.sleep(0.01)
            
            devices = i2c.scan()
            i2c.unlock()
            
            logger.info(f"Found {len(devices)} I2C devices:")
            for addr in devices:
                logger.info(f"  - 0x{addr:02X}")
            
            # Expected devices: 2x PCA9685, 1-2x ADS1115
            if len(devices) >= 3:
                return TestResult("I2C Scan", True, 
                                f"Found {len(devices)} devices")
            else:
                return TestResult("I2C Scan", False,
                                f"Only found {len(devices)} devices, expected ≥3")
        
        except Exception as e:
            return TestResult("I2C Scan", False, str(e))
    
    def test_pwm_controllers(self) -> TestResult:
        """Test PCA9685 PWM controllers"""
        logger.info("Testing PWM controllers...")
        
        try:
            from software.servo_controller import PWMServoController
            
            pwm = PWMServoController()
            
            # Test setting a servo angle
            pwm.set_angle(1, 0, 90)
            time.sleep(0.5)
            
            return TestResult("PWM Controllers", True, 
                            "PCA9685 boards initialized")
        
        except Exception as e:
            return TestResult("PWM Controllers", False, str(e))
    
    def test_serial_servos(self) -> TestResult:
        """Test LX-16A serial bus servos"""
        logger.info("Testing serial bus servos...")
        
        try:
            from software.servo_controller import LX16AServoController
            
            serial_ctrl = LX16AServoController()
            
            # Try to read position from servo ID 1
            pos = serial_ctrl.read_position(1)
            
            if pos is not None:
                return TestResult("Serial Servos", True,
                                f"Servo 1 position: {pos}")
            else:
                return TestResult("Serial Servos", False,
                                "No response from servo 1")
        
        except Exception as e:
            return TestResult("Serial Servos", False, str(e))
    
    def test_camera(self) -> TestResult:
        """Test Raspberry Pi Camera"""
        logger.info("Testing camera...")
        
        try:
            from picamera2 import Picamera2
            
            camera = Picamera2()
            config = camera.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"}
            )
            camera.configure(config)
            camera.start()
            time.sleep(2)
            
            # Capture test frame
            frame = camera.capture_array()
            camera.stop()
            
            if frame.shape == (480, 640, 3):
                return TestResult("Camera", True,
                                f"Captured {frame.shape} frame")
            else:
                return TestResult("Camera", False,
                                f"Unexpected frame shape: {frame.shape}")
        
        except Exception as e:
            return TestResult("Camera", False, str(e))
    
    def test_tactile_sensors(self) -> TestResult:
        """Test FSR tactile sensors"""
        logger.info("Testing tactile sensors...")
        
        try:
            from software.tactile_sensing import TactileSensorArray
            
            sensors = TactileSensorArray(i2c_address=0x48)
            sensors.add_sensor(0, "test_sensor")
            
            # Read sensor
            reading = sensors.read_sensor("test_sensor")
            
            if reading is not None:
                return TestResult("Tactile Sensors", True,
                                f"Reading: {reading.voltage:.3f}V")
            else:
                return TestResult("Tactile Sensors", False,
                                "Failed to read sensor")
        
        except Exception as e:
            return TestResult("Tactile Sensors", False, str(e))
    
    def test_inverse_kinematics(self) -> TestResult:
        """Test IK solver"""
        logger.info("Testing inverse kinematics...")
        
        try:
            from software.kinematics import InverseKinematics
            import numpy as np
            
            ik = InverseKinematics()
            
            # Test reachable target
            solution = ik.solve_ik(0.3, 0.1, 0.2)
            
            if solution is not None:
                # Verify with forward kinematics
                fk_pos = ik.forward_kinematics(solution)
                error = np.sqrt((fk_pos[0]-0.3)**2 + (fk_pos[1]-0.1)**2 + 
                              (fk_pos[2]-0.2)**2)
                
                if error < 0.01:  # 1cm tolerance
                    return TestResult("Inverse Kinematics", True,
                                    f"Error: {error*1000:.1f}mm")
                else:
                    return TestResult("Inverse Kinematics", False,
                                    f"High error: {error*1000:.1f}mm")
            else:
                return TestResult("Inverse Kinematics", False,
                                "No solution found for reachable target")
        
        except Exception as e:
            return TestResult("Inverse Kinematics", False, str(e))
    
    def test_power_system(self) -> TestResult:
        """Test power system voltages"""
        logger.info("Testing power system...")
        
        # This would require additional voltage sensing circuitry
        # For now, just check if we can read serial servo voltage
        try:
            from software.servo_controller import LX16AServoController
            
            serial_ctrl = LX16AServoController()
            voltage = serial_ctrl.read_voltage(1)
            
            if voltage is not None:
                voltage_v = voltage / 1000.0
                if 5.0 <= voltage_v <= 7.0:
                    return TestResult("Power System", True,
                                    f"Servo voltage: {voltage_v:.2f}V")
                else:
                    return TestResult("Power System", False,
                                    f"Abnormal voltage: {voltage_v:.2f}V")
            else:
                return TestResult("Power System", False,
                                "Cannot read servo voltage")
        
        except Exception as e:
            return TestResult("Power System", False, str(e))
    
    def run_all_tests(self) -> bool:
        """Run complete test suite"""
        logger.info("=" * 60)
        logger.info("ARTISAN-1 SYSTEM TEST SUITE")
        logger.info("=" * 60)
        
        tests = [
            ("I2C Bus", self.test_i2c_devices),
            ("PWM Controllers", self.test_pwm_controllers),
            ("Serial Servos", self.test_serial_servos),
            ("Camera", self.test_camera),
            ("Tactile Sensors", self.test_tactile_sensors),
            ("Inverse Kinematics", self.test_inverse_kinematics),
            ("Power System", self.test_power_system),
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name} ---")
            result = test_func()
            self.results[test_name] = result
            
            if result.passed:
                logger.info(f"✓ PASS: {result.message}")
            else:
                logger.error(f"✗ FAIL: {result.message}")
            
            time.sleep(1)
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for r in self.results.values() if r.passed)
        total = len(self.results)
        
        for name, result in self.results.items():
            status = "✓ PASS" if result.passed else "✗ FAIL"
            logger.info(f"{status:8s} | {name:25s} | {result.message}")
        
        logger.info("=" * 60)
        logger.info(f"Results: {passed}/{total} tests passed "
                   f"({100*passed/total:.0f}%)")
        logger.info("=" * 60)
        
        return passed == total


def main():
    """Main test entry point"""
    test_suite = Artisan1TestSuite()
    
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        test_methods = {
            "i2c": test_suite.test_i2c_devices,
            "pwm": test_suite.test_pwm_controllers,
            "serial": test_suite.test_serial_servos,
            "camera": test_suite.test_camera,
            "tactile": test_suite.test_tactile_sensors,
            "ik": test_suite.test_inverse_kinematics,
            "power": test_suite.test_power_system,
        }
        
        if test_name in test_methods:
            result = test_methods[test_name]()
            print(f"\n{'PASS' if result.passed else 'FAIL'}: {result.message}")
            sys.exit(0 if result.passed else 1)
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: {', '.join(test_methods.keys())}")
            sys.exit(1)
    else:
        # Run all tests
        success = test_suite.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
