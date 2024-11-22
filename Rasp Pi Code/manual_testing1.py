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
        try:
            # Get user input for PWM values between 0 and 1
            l = float(input("Enter Lpwm Range (0-1) = "))
            r = float(input("Enter Rpwm Range (0-1) = "))

            # Ensure values are within the valid range
            l = max(0, min(l, 1))
            r = max(0, min(r, 1))

            # Set motor speeds
            leftMotor.forward(l)
            rightMotor.forward(r)

            # Print the PWM values being sent to the motors
            print(f"Left Motor PWM Duty Cycle: {l * 100}%, Right Motor PWM Duty Cycle: {r * 100}%")
            
        except ValueError:
            print("Invalid input! Please enter a number between 0 and 1.")

        # Add a small delay to avoid overwhelming the input loop
        time.sleep(0.1)

except KeyboardInterrupt:
    # Stop the motors when exiting the program
    print("\nStopping motors...")
    leftMotor.stop()
    rightMotor.stop()
    print("Program terminated.")
