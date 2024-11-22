from gpiozero import PhaseEnableMotor
import time

# Define motor control pins
dirA = 17
dirB = 16
pwmA = 18
pwmB = 19

# Initialize the motors with phase and enable pins
leftMotor = PhaseEnableMotor(phase=dirA, enable=pwmA)
rightMotor = PhaseEnableMotor(phase=dirB, enable=pwmB)

try:
    while True:
        # Get user input for motor control
        command = input("Enter command (w/a/d/s): ").strip().lower()

        if command == 'w':
            # Both motors forward at full speed
            leftMotor.forward(1)
            rightMotor.forward(1)
            print("Motors running forward at full speed.")

        elif command == 'a':
            # Left motor at 0.3, right motor at 0.7
            leftMotor.forward(0.3)
            rightMotor.forward(0.7)
            print("Turning left: Left Motor 30%, Right Motor 70%.")

        elif command == 'd':
            # Left motor at 0.7, right motor at 0.3
            leftMotor.forward(0.7)
            rightMotor.forward(0.3)
            print("Turning right: Left Motor 70%, Right Motor 30%.")

        elif command == 's':
            # Both motors stop
            leftMotor.forward(0)
            rightMotor.forward(0)
            print("Motors stopped.")

        else:
            print("Invalid command! Use 'w', 'a', 'd', or 's'.")

        # Add a small delay to avoid overwhelming the loop
        time.sleep(0.1)

except KeyboardInterrupt:
    # Stop the motors when exiting the program
    print("\nStopping motors...")
    leftMotor.stop()
    rightMotor.stop()
    print("Program terminated.")
