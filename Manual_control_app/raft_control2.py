from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO
import picamera2
import io
import threading
import base64
from time import sleep
from gpiozero import PhaseEnableMotor
from time import sleep
import curses

from flask import Flask, request, render_template
from gpiozero import PhaseEnableMotor

app = Flask(__name__)

dirA = 17
dirB = 16
pwmA = 18
pwmB = 19

leftMotor = PhaseEnableMotor(phase=dirA, enable=pwmA)
rightMotor = PhaseEnableMotor(phase=dirB, enable=pwmB)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control():
    direction = request.get_json()['direction']
    is_moving = True

    if direction == 'forward':
        leftMotor.forward(1)
        rightMotor.forward(1)
    elif direction == 'left':
        leftMotor.forward(0.5)
        rightMotor.forward(1)
    elif direction == 'right':
        leftMotor.forward(1)
        rightMotor.forward(0.5)
    else:
        leftMotor.stop()
        rightMotor.stop()
        is_moving = False

    return {'is_moving': is_moving}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)




app = Flask(__name__)
socketio = SocketIO(app)


# Setup Camera
camera = picamera2.Picamera2()
camera.configure(camera.create_preview_configuration(
    main={"size": (320, 320)},
    controls={"FrameDurationLimits": (33333, 33333)}  # 30fps
))
camera.start()

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
