import asyncio
import struct
import network
from machine import Pin, PWM
from mqtt import MQTTClient

class Car:
    
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.driveForward = True
        self.driveBackward = False
        self.driveRight = False
        self.driveLeft = True
        self.motorOn = True
        self.motorOff = False
        
        # Pico board initializations: neopixel, led, buzzer
        self.motor1_a = PWM(Pin(0, Pin.OUT))
        self.motor1_b = PWM(Pin(1, Pin.OUT))
        self.motor1_a.freq(1000)
        self.motor1_b.freq(1000)
        
        self.motor2_a = PWM(Pin(6, Pin.OUT))
        self.motor2_b = PWM(Pin(7, Pin.OUT))
        self.motor2_a.freq(1000)
        self.motor2_b.freq(1000)

        ratio = 1.5

        # Call internet connection
        self.internet_connection()
        self.mqtt_subscribe()


    def mqtt_subscribe(self):
        # MQTT initialization of client and subscribing to topic 'Mater'
        mqtt_broker = 'broker.hivemq.com'
        port = 1883
        topic = 'ME35-24_bhs'
        topic_sub = 'ME35-24_bhs'

        def callback(topic, msg):
            topic, msg = topic.decode(), msg.decode()
            print(msg)

            self.motor1_a.duty_u16(0)
            self.motor2_a.duty_u16(0)
            self.motor1_b.duty_u16(0)
            self.motor2_b.duty_u16(0)
            if msg == "on":
                print('Start')
                self.motorOff = False
                self.motorOn = True
                self.motor_control()
            elif msg == "off":
                print('Stop')
                self.motorOn = False
                self.motorOff = True
                self.motor_control()
            
                
            if float(msg)<-3:
                msgnum=int(float(msg)*(-1)*10000)
                print(msgnum)
                self.motor1_b.duty_u16(msgnum)
                self.motor2_a.duty_u16(msgnum)            
            else: 
                self.motor1_a.duty_u16(0)
                self.motor2_a.duty_u16(0)
                self.motor1_b.duty_u16(0)
                self.motor2_b.duty_u16(0)
        self.client = MQTTClient("Fred", mqtt_broker, port, keepalive=60) #define topic sub later
        self.client.connect()
        print('Connected to %s MQTT broker' % mqtt_broker)
        self.client.set_callback(callback)  # Set the callback for incoming messages
        self.client.subscribe(topic_sub.encode())  # Subscribe to a topic
        print(f'Subscribed to topic {topic_sub}')  # Debug print


    async def check_mqtt(self):
        while True:
            self.client.check_msg()
            await asyncio.sleep(.01)

    def internet_connection(self):
        try:
            self.wlan.active(True)
            self.wlan.connect('Tufts_Robot', '')

            while self.wlan.ifconfig()[0] == '0.0.0.0':
                print('.', end=' ')
                time.sleep(1)

            # We should have a valid IP now via DHCP
            print(self.wlan.ifconfig())
        except Exception as e:
            print("Failed Connection: ", e)
            quit()

    def motor_control(self):
        print("in motor control")
        if self.motorOn:
            print("motor on")
            
        elif self.motorOff:
            self.motor1_a.duty_u16(0)
            self.motor1_b.duty_u16(0)
            print("motor off")
            
    def turn_Right(self):
        if self.driveRight and self.motorOn:
            self.motor1_a.duty_u16(0)
            self.motor1_b.duty_u16(0)
            self.motor2_b.duty_u16(50000) #check if its a negative number-  if negative power b and not a. Write a function that recieved over the network and outputs the power. Quickly tyest the function. Positive or negative? If positive use a, if negative use b. Assume youll be sending numbers from 0 to 80 - map that to 0 63335 - multiply a Kp to that. 
            print("Turning right")

    def turn_Left(self):
        if self.driveLeft and self.motorOn:
            self.motor1_a.duty_u16(50000)
            self.motor2_a.duty_u16(0)
            self.motor2_b.duty_u16(0)
            print("Turning left")
    
    def forward(self):
        if self.driveForward and self.motorOn:
            self.motor1_a.duty_u16(65535)
            self.motor1_b.duty_u16(0)
            print("Forward")

    def backward(self):
        if self.driveBackward and self.motorOn:
            self.motor1_a.duty_u16(50000)
            self.motor1_b.duty_u16(0)
            print("Backward")

    async def main(self):
        asyncio.create_task(self.check_mqtt())
        asyncio.get_event_loop().run_forever()

# Create Car instance
c = Car()

asyncio.run(c.main())
# To run the MQTT loop, you might want to create an asyncio loop here if necessary

