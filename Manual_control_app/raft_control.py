# motor_control.py
from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO
import RPi.GPIO as GPIO
import picamera2
import io
import threading
import base64
from time import sleep

app = Flask(__name__)
socketio = SocketIO(app)

# Motor GPIO pins
LEFT_MOTOR_PWM = 12
LEFT_MOTOR_DIR1 = 16
LEFT_MOTOR_DIR2 = 18

RIGHT_MOTOR_PWM = 13
RIGHT_MOTOR_DIR1 = 22
RIGHT_MOTOR_DIR2 = 24

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_MOTOR_PWM, GPIO.OUT)
GPIO.setup(LEFT_MOTOR_DIR1, GPIO.OUT)
GPIO.setup(LEFT_MOTOR_DIR2, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR_PWM, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR_DIR1, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR_DIR2, GPIO.OUT)

# Setup PWM
left_pwm = GPIO.PWM(LEFT_MOTOR_PWM, 1000)  # 1000 Hz frequency
right_pwm = GPIO.PWM(RIGHT_MOTOR_PWM, 1000)
left_pwm.start(0)
right_pwm.start(0)

# Setup Camera
camera = picamera2.Picamera2()
camera.configure(camera.create_preview_configuration(
    main={"size": (640, 480)},
    controls={"FrameDurationLimits": (33333, 33333)}  # 30fps
))
camera.start()

# Global state
is_moving = False
DEFAULT_SPEED = 50  # Default forward speed (50%)

def set_motor_direction(dir1_pin, dir2_pin, forward=True):
    if forward:
        GPIO.output(dir1_pin, GPIO.HIGH)
        GPIO.output(dir2_pin, GPIO.LOW)
    else:
        GPIO.output(dir1_pin, GPIO.LOW)
        GPIO.output(dir2_pin, GPIO.HIGH)

def generate_frames():
    while True:
        # Capture frame
        frame = camera.capture_array()
        
        # Convert frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = base64.b64encode(buffer.tobytes()).decode('utf-8')
        
        # Emit frame through Socket.IO
        socketio.emit('video_frame', {'frame': frame})
        sleep(0.033)  # ~30fps

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control():
    global is_moving
    direction = request.json.get('direction', 'stop')
    
    if direction == 'forward':
        # Toggle movement state
        is_moving = not is_moving
        
        if is_moving:
            # Start moving forward
            left_pwm.ChangeDutyCycle(DEFAULT_SPEED)
            right_pwm.ChangeDutyCycle(DEFAULT_SPEED)
            set_motor_direction(LEFT_MOTOR_DIR1, LEFT_MOTOR_DIR2, True)
            set_motor_direction(RIGHT_MOTOR_DIR1, RIGHT_MOTOR_DIR2, True)
        else:
            # Stop both motors
            left_pwm.ChangeDutyCycle(0)
            right_pwm.ChangeDutyCycle(0)
    
    elif direction == 'left' and is_moving:
        # Turn left while moving
        left_pwm.ChangeDutyCycle(DEFAULT_SPEED * 0.6)
        right_pwm.ChangeDutyCycle(DEFAULT_SPEED * 1.4)
        set_motor_direction(LEFT_MOTOR_DIR1, LEFT_MOTOR_DIR2, True)
        set_motor_direction(RIGHT_MOTOR_DIR1, RIGHT_MOTOR_DIR2, True)
    
    elif direction == 'right' and is_moving:
        # Turn right while moving
        left_pwm.ChangeDutyCycle(DEFAULT_SPEED * 1.4)
        right_pwm.ChangeDutyCycle(DEFAULT_SPEED * 0.6)
        set_motor_direction(LEFT_MOTOR_DIR1, LEFT_MOTOR_DIR2, True)
        set_motor_direction(RIGHT_MOTOR_DIR1, RIGHT_MOTOR_DIR2, True)
    
    elif direction == 'center' and is_moving:
        # Return to straight forward movement
        left_pwm.ChangeDutyCycle(DEFAULT_SPEED)
        right_pwm.ChangeDutyCycle(DEFAULT_SPEED)
        set_motor_direction(LEFT_MOTOR_DIR1, LEFT_MOTOR_DIR2, True)
        set_motor_direction(RIGHT_MOTOR_DIR1, RIGHT_MOTOR_DIR2, True)
    
    return jsonify({'status': 'success', 'is_moving': is_moving})

if __name__ == '__main__':
    try:
        # Start video streaming in a separate thread
        video_thread = threading.Thread(target=generate_frames)
        video_thread.daemon = True
        video_thread.start()
        
        # Start the Flask-SocketIO app
        socketio.run(app, host='0.0.0.0', port=5000)
    finally:
        camera.stop()
        GPIO.cleanup()