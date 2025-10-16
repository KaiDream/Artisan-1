"""
Computer Vision Module

Implements AI-powered object detection using TensorFlow Lite and OpenCV
for Artisan-1's visual perception system.
"""

import cv2
import numpy as np
import logging
import time
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from pathlib import Path

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    try:
        import tensorflow.lite as tflite
    except ImportError:
        print("Warning: TensorFlow Lite not installed. Run: pip install tflite-runtime")

try:
    from picamera2 import Picamera2
except ImportError:
    print("Warning: picamera2 not installed. Run: pip install picamera2")


logger = logging.getLogger(__name__)


@dataclass
class DetectedObject:
    """Detected object information"""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    center: Tuple[int, int]  # (x, y) center point


class VisionSystem:
    """
    Computer vision system using Raspberry Pi Camera and TensorFlow Lite.
    Implements MobileNetV2-SSD for real-time object detection.
    """
    
    def __init__(self, 
                 model_path: str = "models/mobilenet_ssd_v2.tflite",
                 labels_path: str = "models/coco_labels.txt",
                 camera_resolution: Tuple[int, int] = (640, 480),
                 confidence_threshold: float = 0.5):
        """
        Initialize vision system.
        
        Args:
            model_path: Path to TFLite model file
            labels_path: Path to class labels file
            camera_resolution: Camera resolution (width, height)
            confidence_threshold: Minimum confidence for detections
        """
        self.camera_resolution = camera_resolution
        self.confidence_threshold = confidence_threshold
        
        # Initialize camera
        self._init_camera()
        
        # Load TFLite model
        self._load_model(model_path, labels_path)
        
        logger.info("Vision system initialized")
    
    def _init_camera(self):
        """Initialize Raspberry Pi Camera Module"""
        try:
            self.camera = Picamera2()
            config = self.camera.create_preview_configuration(
                main={"size": self.camera_resolution, "format": "RGB888"}
            )
            self.camera.configure(config)
            self.camera.start()
            time.sleep(2)  # Allow camera to warm up
            logger.info(f"Camera initialized at {self.camera_resolution}")
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            raise
    
    def _load_model(self, model_path: str, labels_path: str):
        """
        Load TFLite model and class labels.
        
        Args:
            model_path: Path to .tflite model
            labels_path: Path to labels text file
        """
        try:
            # Load TFLite model
            self.interpreter = tflite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            
            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            # Get model input size
            self.model_input_size = self.input_details[0]['shape'][1:3]
            
            logger.info(f"Model loaded: {model_path}")
            logger.info(f"Model input size: {self.model_input_size}")
            
            # Load class labels
            if Path(labels_path).exists():
                with open(labels_path, 'r') as f:
                    self.labels = [line.strip() for line in f.readlines()]
                logger.info(f"Loaded {len(self.labels)} class labels")
            else:
                logger.warning(f"Labels file not found: {labels_path}")
                self.labels = []
        
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def capture_frame(self) -> np.ndarray:
        """
        Capture single frame from camera.
        
        Returns:
            RGB image as numpy array
        """
        return self.camera.capture_array()
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for model input.
        
        Args:
            image: Input RGB image
            
        Returns:
            Preprocessed image tensor
        """
        # Resize to model input size
        input_size = (self.model_input_size[1], self.model_input_size[0])
        resized = cv2.resize(image, input_size)
        
        # Normalize to [0, 1] or [-1, 1] depending on model
        # MobileNet SSD typically uses [0, 1]
        normalized = resized.astype(np.float32) / 255.0
        
        # Add batch dimension
        input_tensor = np.expand_dims(normalized, axis=0)
        
        return input_tensor
    
    def detect_objects(self, image: np.ndarray) -> List[DetectedObject]:
        """
        Run object detection on image.
        
        Args:
            image: Input RGB image
            
        Returns:
            List of detected objects
        """
        # Preprocess image
        input_tensor = self.preprocess_image(image)
        
        # Run inference
        self.interpreter.set_tensor(self.input_details[0]['index'], input_tensor)
        self.interpreter.invoke()
        
        # Get detection results
        # Output format for SSD: [boxes, classes, scores, num_detections]
        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]
        num_detections = int(self.interpreter.get_tensor(self.output_details[3]['index'])[0])
        
        # Parse detections
        detections = []
        img_height, img_width = image.shape[:2]
        
        for i in range(num_detections):
            if scores[i] >= self.confidence_threshold:
                # Convert normalized bbox to pixel coordinates
                ymin, xmin, ymax, xmax = boxes[i]
                x = int(xmin * img_width)
                y = int(ymin * img_height)
                w = int((xmax - xmin) * img_width)
                h = int((ymax - ymin) * img_height)
                
                class_id = int(classes[i])
                class_name = self.labels[class_id] if class_id < len(self.labels) else f"Class_{class_id}"
                
                detection = DetectedObject(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=float(scores[i]),
                    bbox=(x, y, w, h),
                    center=(x + w // 2, y + h // 2)
                )
                detections.append(detection)
        
        return detections
    
    def draw_detections(self, image: np.ndarray, 
                       detections: List[DetectedObject]) -> np.ndarray:
        """
        Draw bounding boxes and labels on image.
        
        Args:
            image: Input image
            detections: List of detected objects
            
        Returns:
            Annotated image
        """
        annotated = image.copy()
        
        for det in detections:
            x, y, w, h = det.bbox
            cx, cy = det.center
            
            # Draw bounding box
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw center point
            cv2.circle(annotated, (cx, cy), 5, (255, 0, 0), -1)
            
            # Draw label
            label = f"{det.class_name}: {det.confidence:.2f}"
            cv2.putText(annotated, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return annotated
    
    def find_fabric_corner(self, image: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Detect fabric corner using custom detection or edge detection.
        
        This is a simplified implementation. For production, train a custom
        model to detect "fabric_corner" class.
        
        Args:
            image: Input RGB image
            
        Returns:
            (x, y) pixel coordinates of corner, or None if not found
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Find largest contour (assume it's the fabric)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get approximate polygon
        epsilon = 0.02 * cv2.arcLength(largest_contour, True)
        approx = cv2.approxPolyDP(largest_contour, epsilon, True)
        
        # Find corner points (simplified - just get first vertex)
        if len(approx) >= 3:
            corner = approx[0][0]
            return (int(corner[0]), int(corner[1]))
        
        return None
    
    def pixel_to_3d(self, pixel_coords: Tuple[int, int], 
                    camera_height: float = 0.8,
                    camera_tilt: float = 0.5) -> Tuple[float, float, float]:
        """
        Convert pixel coordinates to approximate 3D world coordinates.
        
        This is a simplified projection. For accurate results, use camera
        calibration and known geometry.
        
        Args:
            pixel_coords: (x, y) pixel coordinates
            camera_height: Camera height above ground in meters
            camera_tilt: Camera tilt angle in radians
            
        Returns:
            (x, y, z) world coordinates in meters
        """
        px, py = pixel_coords
        img_width, img_height = self.camera_resolution
        
        # Convert to normalized image coordinates [-1, 1]
        norm_x = (px - img_width / 2) / (img_width / 2)
        norm_y = (py - img_height / 2) / (img_height / 2)
        
        # Simplified projection (assuming pinhole camera model)
        # This is a rough estimate - calibrate for real use
        focal_length_pixels = img_width  # Rough estimate
        
        # Calculate approximate world coordinates
        # Assumes flat surface at z=0
        z = 0.0  # Table surface
        y = camera_height - norm_y * camera_height / np.tan(camera_tilt)
        x = norm_x * y
        
        return (x, y, z)
    
    def shutdown(self):
        """Shutdown camera"""
        if hasattr(self, 'camera'):
            self.camera.stop()
            logger.info("Camera stopped")


class FabricDetector:
    """
    Specialized detector for fabric corners in textile manipulation task.
    """
    
    def __init__(self, vision_system: VisionSystem):
        """
        Initialize fabric detector.
        
        Args:
            vision_system: VisionSystem instance
        """
        self.vision = vision_system
        self.last_detection_time = 0
        self.detection_cooldown = 0.5  # seconds
    
    def detect_and_localize(self) -> Optional[Dict]:
        """
        Detect fabric corner and return 3D target coordinates.
        
        Returns:
            Dictionary with detection info or None if not found
        """
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_detection_time < self.detection_cooldown:
            return None
        
        # Capture frame
        frame = self.vision.capture_frame()
        
        # Detect fabric corner
        corner_pixel = self.vision.find_fabric_corner(frame)
        
        if corner_pixel is None:
            logger.info("No fabric corner detected")
            return None
        
        # Convert to 3D coordinates
        world_coords = self.vision.pixel_to_3d(corner_pixel)
        
        self.last_detection_time = current_time
        
        detection_info = {
            "pixel_coords": corner_pixel,
            "world_coords": world_coords,
            "timestamp": current_time,
            "frame": frame
        }
        
        logger.info(f"Fabric corner detected at pixel {corner_pixel}, "
                   f"world coords {world_coords}")
        
        return detection_info


if __name__ == "__main__":
    # Test script
    logging.basicConfig(level=logging.INFO)
    
    print("Initializing Vision System...")
    print("Note: Requires TFLite model and camera to be available")
    
    try:
        # Initialize vision system
        vision = VisionSystem()
        
        print("Running object detection for 30 seconds...")
        print("Press Ctrl+C to stop\n")
        
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < 30:
            # Capture and detect
            frame = vision.capture_frame()
            detections = vision.detect_objects(frame)
            
            # Log detections
            if detections:
                print(f"\nFrame {frame_count}: Detected {len(detections)} objects")
                for det in detections:
                    print(f"  - {det.class_name}: {det.confidence:.2f} at {det.center}")
            
            frame_count += 1
            time.sleep(0.5)
        
        # Calculate FPS
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        print(f"\nProcessed {frame_count} frames in {elapsed:.1f}s ({fps:.1f} FPS)")
        
        vision.shutdown()
        print("Test complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
