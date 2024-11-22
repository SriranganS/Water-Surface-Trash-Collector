import cv2
from picamera2 import Picamera2
from ultralytics import YOLO
from gpiozero import PhaseEnableMotor
from time import sleep, time
import signal
import sys

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.previous_error = 0
        self.windup_limit = 10000  # Add windup limit
        self.integral = 0
        self.last_time = time()

    def compute(self, error):
        # Time difference
        current_time = time()
        dt = current_time - self.last_time

        # Prevent division by zero
        if dt <= 0:
            dt = 0.001

        # Proportional term
        p_term = self.kp * error

        # Integral term
        self.integral += error * dt
        self.integral = max(-self.windup_limit, min(self.windup_limit, self.integral))
        i_term = self.ki * self.integral

        # Derivative term
        derivative = (error - self.previous_error) / dt
        d_term = self.kd * derivative

        # Update state
        self.previous_error = error
        self.last_time = current_time

        # Calculate total output
        output = p_term + i_term + d_term

        # Clamp output to [-1, 1]
        return max(-1.0, min(1.0, output))

    def reset(self):
        """Reset the PID controller's state"""
        self.previous_error = 0
        self.integral = 0
        self.last_time = time()

# GPIO setup
dirA = 17
dirB = 16
pwmA = 18
pwmB = 19

leftMotor = PhaseEnableMotor(phase=dirA, enable=pwmA)
rightMotor = PhaseEnableMotor(phase=dirB, enable=pwmB)

# Initialize PID controller
pid = PIDController(kp=0.001, ki=0.0001, kd=0.0001)

# Camera setup
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 1280)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# Load YOLOv8
model = YOLO("yolov8n.pt")
bottle_class_id = 39

def control_motors(pid_output):
    """
    Control motors based on PID output
    pid_output range: [-1, 1]
    """
    if abs(pid_output) < 0.1:  # Dead zone to prevent small oscillations
        leftMotor.stop()
        rightMotor.stop()
        return

    if pid_output > 0:  # Turn right
        left_speed = abs(pid_output)
        right_speed = max(0, abs(pid_output) - 0.5)  # Reduce inner wheel speed
        leftMotor.forward(speed=left_speed)
        if right_speed > 0:
            rightMotor.forward(speed=right_speed)
        else:
            rightMotor.stop()
    else:  # Turn left
        right_speed = abs(pid_output)
        left_speed = max(0, abs(pid_output) - 0.5)  # Reduce inner wheel speed
        rightMotor.forward(speed=right_speed)
        if left_speed > 0:
            leftMotor.forward(speed=left_speed)
        else:
            leftMotor.stop()

def handle_exit(signum, frame):
    """Handle cleanup on program exit"""
    print("\nExiting...")
    leftMotor.stop()
    rightMotor.stop()
    picam2.stop()
    cv2.destroyAllWindows()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, handle_exit)

while True:
    # Capture frame
    frame = picam2.capture_array()
    annotated_frame = frame.copy()

    # Run YOLO detection
    results = model(frame, imgsz=320)

    # Filter for bottle detections
    bottle_detections = [det for det in results[0].boxes if det.cls == bottle_class_id]

    if bottle_detections:
        # Use the first detected bottle
        det = bottle_detections[0]
        x_min, y_min, x_max, y_max = map(int, det.xyxy[0])

        # Draw bounding box
        cv2.rectangle(annotated_frame, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
        cv2.putText(annotated_frame, "Bottle", (x_min, y_min - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Calculate center points
        object_center_x = (x_min + x_max) // 2
        object_center_y = (y_min + y_max) // 2
        camera_center_x = frame.shape[1] // 2
        camera_center_y = frame.shape[0] // 2

        # Draw center line
        cv2.line(annotated_frame, (camera_center_x, camera_center_y), 
                (object_center_x, object_center_y), (0, 0, 255), 2)

        # Calculate error (normalized to frame width)
        x_error = (object_center_x - camera_center_x) / (frame.shape[1] / 2)

        # Get PID output
        pid_output = pid.compute(x_error)

        # Control motors based on PID output
        control_motors(pid_output)

        # Display information
        error_text = f'Error: {x_error:.2f}'
        pid_text = f'PID Output: {pid_output:.2f}'
        cv2.putText(annotated_frame, error_text, (10, frame.shape[0] - 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(annotated_frame, pid_text, (10, frame.shape[0] - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    else:
        # Stop motors if no bottle is detected
        leftMotor.stop()
        rightMotor.stop()
        # Reset PID controller when target is lost
        pid.reset()

    # Display the frame
    cv2.imshow("Camera", annotated_frame)

    if cv2.waitKey(1) == ord("q"):
        break

# Cleanup (in case of manual break)
handle_exit(None, None)
