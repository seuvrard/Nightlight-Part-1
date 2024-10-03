import machine
from machine import Pin, PWM
import time

# Motor 1 (M1A = Pin 0, M1B = Pin 1)
motor1_a = PWM(Pin(0, Pin.OUT))
motor1_b = PWM(Pin(1, Pin.OUT))
motor1_a.freq(1000)
motor1_b.freq(1000)

# Motor 2 (M2A = Pin 2, M2B = Pin 3)
motor2_a = PWM(Pin(2, Pin.OUT))
motor2_b = PWM(Pin(3, Pin.OUT))
motor2_a.freq(1000)
motor2_b.freq(1000)

def motor_forward():
    # Motor 1 Forward: M1A = High, M1B = Low
    motor1_a.duty_u16(50000)
    motor1_b.duty_u16(0)
    # Motor 2 Forward: M2A = High, M2B = Low
    
    motor2_a.duty_u16(0)
    motor2_b.duty_u16(50000)
    
    print("Motors moving forward")

def motor_backward():
    # Motor 1 Forward: M1A = High, M1B = Low
    motor1_a.duty_u16(0)
    motor1_b.duty_u16(50000)
    # Motor 2 Forward: M2A = High, M2B = Low
    
    motor2_a.duty_u16(50000)
    motor2_b.duty_u16(0)
    
    print("Motors moving backward")

def motor_stop():
    motor1_a.duty_u16(0)
    motor1_b.duty_u16(0)
    # Motor 2 Forward: M2A = High, M2B = Low
    
    motor2_a.duty_u16(0)
    motor2_b.duty_u16(0)
    
    print("Motors stopped")

# Test motor forward and backward
def test_motors():
    try:
        print("Testing forward motion")
        motor_forward()
        time.sleep(5)  # Run forward for 5 seconds
        
        print("Testing backward motion")
        motor_backward()
        time.sleep(5)  # Run backward for 5 seconds
        
        print("Stopping motors")
        motor_stop()
        
    except KeyboardInterrupt:
        print("Test interrupted")
        motor_stop()

# Run the motor test
test_motors()
