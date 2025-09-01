ccfrom adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)
esc = kit.servo[1]

neutro = 80

esc.set_pulse_width_range(1000, 2000)

# Armar el ESC
print("Armando ESC...")
esc.angle = 80
time.sleep(1)

def retroceder(velocidad =64):
    esc.angle = 80
    time.sleep(1)
    esc.angle = 65
    time.sleep(1)
    esc.angle = 80
    time.sleep(1)
    esc.angle = velocidad
    
def adelante(velocidad=102):
    esc.angle= velocidad
    
def parar (velocidad = 80):
    esc.angle = velocidad

def doblar (velocidad = 101):
      esc.angle = 80
      time.sleep (1)
      esc.angle= velocidad