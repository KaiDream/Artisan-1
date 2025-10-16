"""
Inverse Kinematics Module

Implements IK solver for Artisan-1's 5-DOF arm to enable
visually-guided reaching and manipulation.
"""

import numpy as np
import logging
from typing import Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class ArmSide(Enum):
    """Which arm to control"""
    LEFT = "left"
    RIGHT = "right"


@dataclass
class ArmConfiguration:
    """DH parameters and joint limits for robot arm"""
    # Link lengths in meters
    shoulder_offset: float = 0.05  # Shoulder to upper arm joint
    upper_arm_length: float = 0.25  # Upper arm (humerus)
    forearm_length: float = 0.20  # Forearm (radius/ulna)
    hand_length: float = 0.10  # Hand to fingertip
    
    # Joint limits in degrees
    shoulder_pitch_min: float = -90
    shoulder_pitch_max: float = 180
    shoulder_roll_min: float = -90
    shoulder_roll_max: float = 90
    shoulder_yaw_min: float = -90
    shoulder_yaw_max: float = 90
    elbow_min: float = 0
    elbow_max: float = 150
    wrist_min: float = -90
    wrist_max: float = 90


@dataclass
class JointAngles:
    """Joint angles for 5-DOF arm"""
    shoulder_pitch: float  # Forward/backward
    shoulder_roll: float   # Up/down
    shoulder_yaw: float    # Rotation
    elbow: float          # Bend
    wrist: float          # Rotation


class InverseKinematics:
    """
    Inverse kinematics solver for Artisan-1's 5-DOF arm.
    
    Uses geometric approach for computational efficiency on Raspberry Pi.
    For more complex scenarios, consider FABRIK or Jacobian methods.
    """
    
    def __init__(self, config: Optional[ArmConfiguration] = None):
        """
        Initialize IK solver.
        
        Args:
            config: Arm configuration parameters
        """
        self.config = config if config else ArmConfiguration()
        logger.info("IK Solver initialized")
    
    def forward_kinematics(self, angles: JointAngles) -> Tuple[float, float, float]:
        """
        Calculate end-effector position from joint angles (FK).
        
        Args:
            angles: Joint angles in degrees
            
        Returns:
            (x, y, z) position in meters
        """
        # Convert to radians
        sp = np.radians(angles.shoulder_pitch)
        sr = np.radians(angles.shoulder_roll)
        sy = np.radians(angles.shoulder_yaw)
        e = np.radians(angles.elbow)
        w = np.radians(angles.wrist)
        
        # Simplified FK calculation
        # This is a geometric approach - for production use DH parameters
        
        # Calculate reach in horizontal plane
        horizontal_reach = (
            self.config.upper_arm_length * np.cos(sr) * np.cos(sp) +
            self.config.forearm_length * np.cos(sr + e) * np.cos(sp) +
            self.config.hand_length * np.cos(sr + e) * np.cos(sp)
        )
        
        # Calculate height
        height = (
            self.config.upper_arm_length * np.sin(sr) +
            self.config.forearm_length * np.sin(sr + e) +
            self.config.hand_length * np.sin(sr + e)
        )
        
        # Apply yaw rotation
        x = horizontal_reach * np.cos(sy)
        y = horizontal_reach * np.sin(sy)
        z = height
        
        return (x, y, z)
    
    def solve_ik(self, 
                 target_x: float, 
                 target_y: float, 
                 target_z: float,
                 arm_side: ArmSide = ArmSide.LEFT) -> Optional[JointAngles]:
        """
        Solve inverse kinematics for target position.
        
        Uses geometric approach for 5-DOF arm. This is a simplified
        implementation - for production, consider FABRIK or numerical methods.
        
        Args:
            target_x: Target X coordinate in meters
            target_y: Target Y coordinate in meters
            target_z: Target Z coordinate in meters
            arm_side: Which arm (affects shoulder yaw calculation)
            
        Returns:
            JointAngles solution or None if unreachable
        """
        # Calculate distance to target
        target_distance = np.sqrt(target_x**2 + target_y**2 + target_z**2)
        
        # Check if target is reachable
        max_reach = (self.config.upper_arm_length + 
                    self.config.forearm_length + 
                    self.config.hand_length)
        
        if target_distance > max_reach:
            logger.warning(f"Target unreachable: {target_distance:.3f}m > {max_reach:.3f}m")
            return None
        
        # Solve shoulder yaw (rotation in horizontal plane)
        shoulder_yaw = np.degrees(np.arctan2(target_y, target_x))
        
        # Mirror for right arm
        if arm_side == ArmSide.RIGHT:
            shoulder_yaw = -shoulder_yaw
        
        # Calculate horizontal distance
        horizontal_dist = np.sqrt(target_x**2 + target_y**2)
        
        # Solve for shoulder pitch and roll using 2D IK in sagittal plane
        # Simplify to 2-link arm (upper + forearm+hand)
        l1 = self.config.upper_arm_length
        l2 = self.config.forearm_length + self.config.hand_length
        
        # Target in arm's local 2D plane
        r = np.sqrt(horizontal_dist**2 + target_z**2)
        
        # Check reachability in 2D plane
        if r > l1 + l2 or r < abs(l1 - l2):
            logger.warning("Target unreachable in 2D plane")
            return None
        
        # Law of cosines for elbow angle
        cos_elbow = (l1**2 + l2**2 - r**2) / (2 * l1 * l2)
        cos_elbow = np.clip(cos_elbow, -1, 1)  # Numerical stability
        elbow_angle = np.degrees(np.arccos(cos_elbow))
        
        # Calculate shoulder angles
        alpha = np.arctan2(target_z, horizontal_dist)
        beta = np.arccos((l1**2 + r**2 - l2**2) / (2 * l1 * r))
        
        shoulder_roll = np.degrees(alpha + beta)
        shoulder_pitch = 0  # Simplified - can be adjusted for orientation
        
        # Wrist rotation (simplified - keep hand level)
        wrist_rotation = 0
        
        # Create solution
        solution = JointAngles(
            shoulder_pitch=shoulder_pitch,
            shoulder_roll=shoulder_roll,
            shoulder_yaw=shoulder_yaw,
            elbow=elbow_angle,
            wrist=wrist_rotation
        )
        
        # Check joint limits
        if not self._check_joint_limits(solution):
            logger.warning("Solution violates joint limits")
            return None
        
        logger.info(f"IK solution found for target ({target_x:.3f}, {target_y:.3f}, {target_z:.3f})")
        
        return solution
    
    def _check_joint_limits(self, angles: JointAngles) -> bool:
        """
        Check if joint angles are within limits.
        
        Args:
            angles: Joint angles to check
            
        Returns:
            True if all angles within limits
        """
        checks = [
            (self.config.shoulder_pitch_min <= angles.shoulder_pitch <= 
             self.config.shoulder_pitch_max),
            (self.config.shoulder_roll_min <= angles.shoulder_roll <= 
             self.config.shoulder_roll_max),
            (self.config.shoulder_yaw_min <= angles.shoulder_yaw <= 
             self.config.shoulder_yaw_max),
            (self.config.elbow_min <= angles.elbow <= 
             self.config.elbow_max),
            (self.config.wrist_min <= angles.wrist <= 
             self.config.wrist_max),
        ]
        
        return all(checks)
    
    def solve_ik_with_orientation(self,
                                  target_x: float,
                                  target_y: float,
                                  target_z: float,
                                  approach_angle: float = 0.0,
                                  arm_side: ArmSide = ArmSide.LEFT) -> Optional[JointAngles]:
        """
        Solve IK with desired end-effector orientation.
        
        Args:
            target_x: Target X in meters
            target_y: Target Y in meters  
            target_z: Target Z in meters
            approach_angle: Desired approach angle in degrees (0 = horizontal)
            arm_side: Which arm to use
            
        Returns:
            Joint angles or None if unreachable
        """
        # Adjust target to account for hand length at desired angle
        approach_rad = np.radians(approach_angle)
        adjusted_x = target_x - self.config.hand_length * np.cos(approach_rad)
        adjusted_z = target_z - self.config.hand_length * np.sin(approach_rad)
        
        # Solve for wrist position
        solution = self.solve_ik(adjusted_x, target_y, adjusted_z, arm_side)
        
        if solution:
            # Adjust wrist to achieve desired orientation
            solution.wrist = approach_angle
        
        return solution


class ArmController:
    """
    High-level arm controller that combines IK with servo control.
    """
    
    def __init__(self, servo_controller, ik_solver: Optional[InverseKinematics] = None):
        """
        Initialize arm controller.
        
        Args:
            servo_controller: Instance of ArtisanServoController
            ik_solver: IK solver instance (creates default if None)
        """
        self.servo = servo_controller
        self.ik = ik_solver if ik_solver else InverseKinematics()
        logger.info("Arm Controller initialized")
    
    def move_to_position(self,
                        target_x: float,
                        target_y: float,
                        target_z: float,
                        arm_side: ArmSide = ArmSide.LEFT,
                        movement_time_ms: int = 1000) -> bool:
        """
        Move arm end-effector to target position.
        
        Args:
            target_x: Target X coordinate in meters
            target_y: Target Y coordinate in meters
            target_z: Target Z coordinate in meters
            arm_side: Which arm to move
            movement_time_ms: Movement duration
            
        Returns:
            True if successful, False if target unreachable
        """
        # Solve IK
        solution = self.ik.solve_ik(target_x, target_y, target_z, arm_side)
        
        if solution is None:
            logger.error("IK solution failed - target unreachable")
            return False
        
        # Map to servo joints
        from servo_controller import JointLocation
        
        if arm_side == ArmSide.LEFT:
            joints = {
                JointLocation.LEFT_SHOULDER_PITCH: solution.shoulder_pitch,
                JointLocation.LEFT_SHOULDER_ROLL: solution.shoulder_roll,
                JointLocation.LEFT_SHOULDER_YAW: solution.shoulder_yaw,
                JointLocation.LEFT_ELBOW: solution.elbow,
                JointLocation.LEFT_WRIST: solution.wrist,
            }
        else:
            joints = {
                JointLocation.RIGHT_SHOULDER_PITCH: solution.shoulder_pitch,
                JointLocation.RIGHT_SHOULDER_ROLL: solution.shoulder_roll,
                JointLocation.RIGHT_SHOULDER_YAW: solution.shoulder_yaw,
                JointLocation.RIGHT_ELBOW: solution.elbow,
                JointLocation.RIGHT_WRIST: solution.wrist,
            }
        
        # Command servos
        for joint, angle in joints.items():
            self.servo.set_joint_angle(joint, angle, movement_time_ms)
        
        logger.info(f"Commanded {arm_side.value} arm to ({target_x:.3f}, {target_y:.3f}, {target_z:.3f})")
        return True
    
    def reach_and_grasp(self,
                       target_x: float,
                       target_y: float,
                       target_z: float,
                       arm_side: ArmSide = ArmSide.LEFT) -> bool:
        """
        Reach to position and execute grasp.
        
        Args:
            target_x: Target X in meters
            target_y: Target Y in meters
            target_z: Target Z in meters
            arm_side: Which arm to use
            
        Returns:
            True if grasp attempted successfully
        """
        from servo_controller import JointLocation
        import time
        
        # Move to pre-grasp position (above target)
        pre_grasp_z = target_z + 0.05  # 5cm above
        success = self.move_to_position(target_x, target_y, pre_grasp_z, arm_side, 1500)
        
        if not success:
            return False
        
        time.sleep(1.5)  # Wait for movement
        
        # Open hand
        hand_fingers = (JointLocation.LEFT_HAND_FINGERS if arm_side == ArmSide.LEFT 
                       else JointLocation.RIGHT_HAND_FINGERS)
        hand_thumb = (JointLocation.LEFT_HAND_THUMB if arm_side == ArmSide.LEFT
                     else JointLocation.RIGHT_HAND_THUMB)
        
        self.servo.set_joint_angle(hand_fingers, 0)  # Open
        self.servo.set_joint_angle(hand_thumb, 0)
        time.sleep(0.5)
        
        # Descend to target
        self.move_to_position(target_x, target_y, target_z, arm_side, 800)
        time.sleep(0.8)
        
        # Close grasp
        self.servo.set_joint_angle(hand_fingers, 90)  # Close
        self.servo.set_joint_angle(hand_thumb, 90)
        time.sleep(0.5)
        
        # Lift
        self.move_to_position(target_x, target_y, target_z + 0.10, arm_side, 1000)
        
        logger.info(f"Grasp sequence completed for {arm_side.value} arm")
        return True


if __name__ == "__main__":
    # Test script
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Inverse Kinematics Solver...\n")
    
    ik = InverseKinematics()
    
    # Test FK
    test_angles = JointAngles(
        shoulder_pitch=0,
        shoulder_roll=45,
        shoulder_yaw=0,
        elbow=90,
        wrist=0
    )
    
    end_pos = ik.forward_kinematics(test_angles)
    print(f"Forward Kinematics Test:")
    print(f"  Joint angles: {test_angles}")
    print(f"  End position: ({end_pos[0]:.3f}, {end_pos[1]:.3f}, {end_pos[2]:.3f}) m\n")
    
    # Test IK
    target_positions = [
        (0.30, 0.10, 0.20),
        (0.25, -0.15, 0.15),
        (0.40, 0.00, 0.10),
    ]
    
    print("Inverse Kinematics Tests:")
    for i, (x, y, z) in enumerate(target_positions):
        print(f"\nTest {i+1}: Target ({x:.2f}, {y:.2f}, {z:.2f}) m")
        solution = ik.solve_ik(x, y, z)
        
        if solution:
            print(f"  Solution found:")
            print(f"    Shoulder Pitch: {solution.shoulder_pitch:.1f}°")
            print(f"    Shoulder Roll:  {solution.shoulder_roll:.1f}°")
            print(f"    Shoulder Yaw:   {solution.shoulder_yaw:.1f}°")
            print(f"    Elbow:          {solution.elbow:.1f}°")
            print(f"    Wrist:          {solution.wrist:.1f}°")
            
            # Verify with FK
            verify_pos = ik.forward_kinematics(solution)
            error = np.sqrt((verify_pos[0]-x)**2 + (verify_pos[1]-y)**2 + (verify_pos[2]-z)**2)
            print(f"  Verification error: {error*1000:.1f} mm")
        else:
            print("  No solution found (unreachable)")
    
    print("\nIK Solver test complete!")
