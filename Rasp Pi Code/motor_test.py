# from gpiozero import PWMOutputDevice, DigitalOutputDevice
# import time


# # Initialize motors using correct MDD10 pins from the board
# # Motor 2
# M2_PWM = PWMOutputDevice(6)  # D6 - PWM control
# M2_DIR = DigitalOutputDevice(12)  # D12 - Direction control


# def set_motor_speed(pwm_pin, dir_pin, speed):
#     """
#     Set motor speed and direction
#     speed: -1.0 to 1.0 (negative for reverse)
#     """
#     if speed >= 0:
#         dir_pin.off()  # Forward
#         pwm_pin.value = speed
#     else:
#         dir_pin.on()  # Reverse
#         pwm_pin.value = -speed


# # Test the motor
# try:
#     print("Testing Motor 2...")
#     print("Forward at 50% speed for 2 seconds")
#     set_motor_speed(M2_PWM, M2_DIR, 0.5)
#     time.sleep(2)

#     print("Stopping for 1 second")
#     set_motor_speed(M2_PWM, M2_DIR, 0)
#     time.sleep(1)

#     print("Reverse at 50% speed for 2 seconds")
#     set_motor_speed(M2_PWM, M2_DIR, -0.5)
#     time.sleep(2)

#     print("Stopping")
#     set_motor_speed(M2_PWM, M2_DIR, 0)

# except KeyboardInterrupt:
#     print("Program stopped by user")
# finally:
#     # Clean up
#     M2_PWM.value = 0
#     M2_DIR.off()

from gpiozero import DigitalOutputDevice
from time import sleep

dir = DigitalOutputDevice(16)
pwm = DigitalOutputDevice(19)

dir.off()
pwm.off()

sleep(2)

pwm.on()

sleep(5)

dir.on()

sleep(5)

pwm.off()

sleep(5)