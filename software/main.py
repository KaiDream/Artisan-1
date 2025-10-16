"""
Main Control System for Artisan-1

Integrates all subsystems for autonomous textile manipulation demonstration.
"""

import time
import logging
import signal
import sys
from typing import Optional
from enum import Enum

from servo_controller import ArtisanServoController, JointLocation
from tactile_sensing import ArtisanHandSensing
from vision import VisionSystem, FabricDetector
from kinematics import InverseKinematics, ArmController, ArmSide


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('artisan1.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RobotState(Enum):
    """Robot operational states"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    CALIBRATING = "calibrating"
    SCANNING = "scanning"
    REACHING = "reaching"
    GRASPING = "grasping"
    LIFTING = "lifting"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class Artisan1Robot:
    """
    Main control class for Artisan-1 humanoid robot.
    
    Manages all subsystems and implements high-level behaviors including
    the visually-guided textile corner grasping demonstration.
    """
    
    def __init__(self):
        """Initialize Artisan-1 robot"""
        logger.info("=" * 60)
        logger.info("Initializing Artisan-1 Robot Control System")
        logger.info("=" * 60)
        
        self.state = RobotState.INITIALIZING
        self.running = True
        
        # Initialize subsystems
        try:
            # Servo control
            logger.info("Initializing servo controller...")
            self.servo_controller = ArtisanServoController()
            
            # Tactile sensing
            logger.info("Initializing tactile sensors...")
            self.tactile_sensors = ArtisanHandSensing()
            
            # Vision system
            logger.info("Initializing vision system...")
            self.vision = VisionSystem(
                confidence_threshold=0.6
            )
            self.fabric_detector = FabricDetector(self.vision)
            
            # Kinematics and arm control
            logger.info("Initializing inverse kinematics...")
            self.ik_solver = InverseKinematics()
            self.arm_controller = ArmController(self.servo_controller, self.ik_solver)
            
            self.state = RobotState.IDLE
            logger.info("All subsystems initialized successfully!")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            self.state = RobotState.ERROR
            raise
    
    def calibrate_sensors(self):
        """Calibrate all sensors"""
        logger.info("Starting sensor calibration...")
        self.state = RobotState.CALIBRATING
        
        try:
            # Ensure hands are open for tactile calibration
            logger.info("Opening hands for calibration...")
            self.servo_controller.set_joint_angle(JointLocation.LEFT_HAND_FINGERS, 0)
            self.servo_controller.set_joint_angle(JointLocation.LEFT_HAND_THUMB, 0)
            self.servo_controller.set_joint_angle(JointLocation.RIGHT_HAND_FINGERS, 0)
            self.servo_controller.set_joint_angle(JointLocation.RIGHT_HAND_THUMB, 0)
            
            time.sleep(2)
            
            # Calibrate tactile sensors
            logger.info("Calibrating tactile sensors...")
            self.tactile_sensors.calibrate()
            
            logger.info("Calibration complete!")
            self.state = RobotState.IDLE
            
        except Exception as e:
            logger.error(f"Calibration failed: {e}")
            self.state = RobotState.ERROR
    
    def move_to_neutral_pose(self):
        """Move robot to neutral standing pose"""
        logger.info("Moving to neutral pose...")
        
        try:
            # Head centered
            self.servo_controller.set_joint_angle(JointLocation.HEAD_PAN, 90)
            self.servo_controller.set_joint_angle(JointLocation.HEAD_TILT, 90)
            
            # Arms at sides
            neutral_angles = {
                # Left arm
                JointLocation.LEFT_SHOULDER_PITCH: 90,
                JointLocation.LEFT_SHOULDER_ROLL: 45,
                JointLocation.LEFT_SHOULDER_YAW: 90,
                JointLocation.LEFT_ELBOW: 45,
                JointLocation.LEFT_WRIST: 90,
                # Right arm
                JointLocation.RIGHT_SHOULDER_PITCH: 90,
                JointLocation.RIGHT_SHOULDER_ROLL: 45,
                JointLocation.RIGHT_SHOULDER_YAW: 90,
                JointLocation.RIGHT_ELBOW: 45,
                JointLocation.RIGHT_WRIST: 90,
            }
            
            for joint, angle in neutral_angles.items():
                self.servo_controller.set_joint_angle(joint, angle, time_ms=2000)
            
            time.sleep(2)
            logger.info("Neutral pose achieved")
            
        except Exception as e:
            logger.error(f"Failed to reach neutral pose: {e}")
    
    def fabric_corner_grasp_demo(self, max_attempts: int = 3) -> bool:
        """
        Execute the visually-guided textile corner grasping demonstration.
        
        This is the capstone task that integrates vision, IK, and tactile sensing.
        
        Args:
            max_attempts: Maximum number of grasp attempts
            
        Returns:
            True if grasp successful, False otherwise
        """
        logger.info("=" * 60)
        logger.info("STARTING FABRIC CORNER GRASP DEMONSTRATION")
        logger.info("=" * 60)
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"\nAttempt {attempt}/{max_attempts}")
            
            # Step 1: Visual Detection
            logger.info("Step 1: Scanning for fabric corner...")
            self.state = RobotState.SCANNING
            
            detection = self.fabric_detector.detect_and_localize()
            
            if detection is None:
                logger.warning("No fabric corner detected")
                time.sleep(1)
                continue
            
            target_world = detection["world_coords"]
            logger.info(f"Fabric corner detected at {target_world}")
            
            # Step 2: Reach to target
            logger.info("Step 2: Reaching to target...")
            self.state = RobotState.REACHING
            
            success = self.arm_controller.reach_and_grasp(
                target_world[0],
                target_world[1],
                target_world[2],
                arm_side=ArmSide.LEFT
            )
            
            if not success:
                logger.warning("Failed to reach target")
                continue
            
            # Step 3: Tactile confirmation
            logger.info("Step 3: Checking grasp with tactile sensors...")
            self.state = RobotState.GRASPING
            
            time.sleep(1)  # Allow sensors to stabilize
            
            grasp_successful = self.tactile_sensors.check_left_grasp(threshold=0.5)
            
            if grasp_successful:
                logger.info("✓ GRASP CONFIRMED by tactile sensors!")
                
                # Step 4: Lift fabric
                logger.info("Step 4: Lifting fabric corner...")
                self.state = RobotState.LIFTING
                
                self.arm_controller.move_to_position(
                    target_world[0],
                    target_world[1],
                    target_world[2] + 0.15,  # Lift 15cm
                    arm_side=ArmSide.LEFT,
                    movement_time_ms=1500
                )
                
                time.sleep(2)
                
                logger.info("=" * 60)
                logger.info("DEMONSTRATION SUCCESSFUL!")
                logger.info("=" * 60)
                
                self.state = RobotState.IDLE
                return True
            
            else:
                logger.warning("✗ Grasp failed - no tactile feedback")
                # Open hand and retry
                self.servo_controller.set_joint_angle(JointLocation.LEFT_HAND_FINGERS, 0)
                self.servo_controller.set_joint_angle(JointLocation.LEFT_HAND_THUMB, 0)
                time.sleep(1)
        
        logger.error("Demonstration failed after maximum attempts")
        self.state = RobotState.IDLE
        return False
    
    def emergency_stop(self):
        """Emergency stop - halt all motion"""
        logger.warning("!!! EMERGENCY STOP ACTIVATED !!!")
        self.state = RobotState.ERROR
        self.servo_controller.emergency_stop()
        self.running = False
    
    def shutdown(self):
        """Graceful shutdown of all systems"""
        logger.info("Shutting down Artisan-1...")
        self.state = RobotState.SHUTDOWN
        
        try:
            # Stop all servos
            self.servo_controller.shutdown()
            
            # Close vision system
            self.vision.shutdown()
            
            logger.info("Shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def run_demo_sequence(self):
        """Run complete demonstration sequence"""
        logger.info("Starting demonstration sequence...")
        
        # Calibrate sensors
        self.calibrate_sensors()
        
        # Move to neutral pose
        self.move_to_neutral_pose()
        
        # Wait for user confirmation
        logger.info("\nPlace fabric on table with visible corner...")
        logger.info("Press Enter when ready (or Ctrl+C to abort)")
        try:
            input()
        except KeyboardInterrupt:
            logger.info("Demo aborted by user")
            return
        
        # Execute fabric grasp demo
        success = self.fabric_corner_grasp_demo()
        
        if success:
            logger.info("\n🎉 Demonstration completed successfully!")
        else:
            logger.info("\n❌ Demonstration did not complete successfully")
        
        # Return to neutral
        self.move_to_neutral_pose()


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global robot
    logger.info("\nInterrupt received, shutting down...")
    if robot:
        robot.emergency_stop()
        robot.shutdown()
    sys.exit(0)


# Global robot instance for signal handler
robot: Optional[Artisan1Robot] = None


def main():
    """Main entry point"""
    global robot
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Initialize robot
        robot = Artisan1Robot()
        
        # Run demonstration
        robot.run_demo_sequence()
        
        # Graceful shutdown
        robot.shutdown()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        
        if robot:
            robot.emergency_stop()
            robot.shutdown()
        
        sys.exit(1)


if __name__ == "__main__":
    main()
