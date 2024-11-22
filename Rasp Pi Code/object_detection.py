import cv2
from picamera2 import Picamera2
from ultralytics import YOLO
from gpiozero import Motor, Robot

# Set up the camera with Picam
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 1280)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

# Load YOLOv8
model = YOLO("yolov8n.pt")

# Define the 'bottle' class ID
bottle_class_id = 39  # Standard ID for 'bottle' in COCO dataset

while True:
    # Capture a frame from the camera
    frame = picam2.capture_array()
   
    # Initialize annotated_frame with the original frame
    annotated_frame = frame.copy()

    # Run YOLO model on the captured frame and store the results
    results = model(frame, imgsz=320)  # Adjust resolution if needed
   
    # Filter for 'bottle' detections
    bottle_detections = [det for det in results[0].boxes if det.cls == bottle_class_id]
   
    # Proceed only if bottles are detected
    if bottle_detections:
        for det in bottle_detections:
            x_min, y_min, x_max, y_max = map(int, det.xyxy[0])  # Bounding box coordinates
            cv2.rectangle(annotated_frame, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)  # Red box
            label = "Bottle"
            cv2.putText(annotated_frame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
           
            # Calculate the object center
            object_center_x = (x_min + x_max) // 2
            object_center_y = (y_min + y_max) // 2
           
            # Draw a line from the camera center to the object center
            camera_center_x = frame.shape[1] // 2
            camera_center_y = frame.shape[0] // 2
            cv2.line(annotated_frame, (camera_center_x, camera_center_y), (object_center_x, object_center_y), (0, 0, 255), 2)
           
            # Calculate the horizontal distance (x_distance)
            x_distance = object_center_x - camera_center_x
            distance_text = f'X Distance: {x_distance}px'
           
            # Display x_distance on the frame
            cv2.putText(annotated_frame, distance_text, (10, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Display the resulting frame
    cv2.imshow("Camera", annotated_frame)

    # Exit the program if 'q' is pressed
    if cv2.waitKey(1) == ord("q"):
        break

# Close all windows
cv2.destroyAllWindows()
