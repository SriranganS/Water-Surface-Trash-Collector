from gpiozero import Robot, PhaseEnableMotor
from time import sleep

dirA = 17
dirB = 16
pwmA = 18
pwmB = 19

robot = Robot(
    left=PhaseEnableMotor(phase=dirA, enable=pwmA),
    right=PhaseEnableMotor(phase=dirB, enable=pwmB),
)

for i in range(4):
    robot.left()
    sleep(5)
    robot.right()
    sleep(5)
    robot.forward()
    sleep(5)
