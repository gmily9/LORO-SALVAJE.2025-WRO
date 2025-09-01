import RPi.GPIO as GPIO
import time

class Ultrasonido:
    def _init_(self, sensors):
        self.sensors = sensors
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for sensor in self.sensors.values():
            GPIO.setup(sensor["TRIG"], GPIO.OUT)
            GPIO.setup(sensor["ECHO"], GPIO.IN)
            GPIO.output(sensor["TRIG"], False)

        time.sleep(2)
        self.distancias_iniciales = self.obtener_distancias_iniciales()

    def medir_distancia(self, trig_pin, echo_pin):
        GPIO.output(trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(trig_pin, False)

        start_time = time.time()
        stop = time.time()
        timeout = time.time() + 0.04
        
        while GPIO.input(echo_pin) == 0 and time.time() < timeout:
            start_time = time.time()

        while GPIO.input(echo_pin) == 1 and time.time() < timeout:
            stop = time.time()

        elapsed = stop - start_time
        distancia = (elapsed * 34300) / 2
        return round(distancia, 2)

    def obtener_distancias_iniciales(self):
        distancias_iniciales = {}
        for nombre, sensor in self.sensors.items():
            distancia = self.medir_distancia(sensor["TRIG"], sensor["ECHO"])
            distancias_iniciales[nombre] = distancia
            time.sleep(0.1)
        return distancias_iniciales

    def obtener_distancias(self):
        distancias = {}
        variaciones = {}
        for nombre, sensor in self.sensors.items():
            distancia = self.medir_distancia(sensor["TRIG"], sensor["ECHO"])
            distancias[nombre] = distancia
            variaciones[nombre] = distancia - self.distancias_iniciales[nombre]
            time.sleep(0.1)
        return distancias, variaciones