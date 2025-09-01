import time
from mpu6050 import mpu6050
from ultrasonidomod import Ultrasonido
from movimiento import adelante, retroceder, parar, doblar
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit

sensors = {
    "izq": {"TRIG": 17, "ECHO": 6},
    "cen": {"TRIG": 23, "ECHO": 24},
    "der": {"TRIG": 5, "ECHO": 27}
}

ultrasonido = Ultrasonido(sensors)

DISTANCIA_VACIO = 100
UMBRAL_FRONTAL = 35         # cm: se considera vacio lateral (esquina)
FACTOR = 3.0                # grados por cm de variacion lateral
RETARDO_GIRO = 1.5

class GyroSteering:
    def _init_(self, servo_channel=0, esc_channel=1, Kp=0.6, Ki=0.0, Kd=0.1, servo_min=60, servo_max=120):
        self.sensor = mpu6050(0x68)
        self.kit = ServoKit(channels=16)
        self.servo_channel = servo_channel
        self.servo_min = servo_min
        self.servo_max = servo_max
        self.last_servo_angle = 90
        self.esc_channel = esc_channel
        self.esc = self.kit.servo[esc_channel]
        self.esc.set_pulse_width_range(1000, 2000)
        self.neutro = 80
        self.armar_esc()
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.integral = 0.0
        self.ultimo_error = 0.0
        self.angle_z = 0.0
        self.last_time = time.time()
        self.angulo_deseado = 0.0

    def armar_esc(self):
        self.esc.angle = self.neutro
        time.sleep(1)

    def reset_yaw(self):
        self.angle_z = 0.0
        self.last_time = time.time()
        self.integral = 0.0
        self.ultimo_error = 0.0
        self.angulo_deseado = 0.0

    def get_angle_z(self):
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        gyro_data = self.sensor.get_gyro_data()
        self.angle_z += gyro_data['z'] * dt
        return self.angle_z, dt

    def pid_control(self, valor_actual, dt):
        error = self.angulo_deseado - valor_actual
        if abs(error) < 0.5:
            error = 0
        self.integral += error * dt
        derivada = (error - self.ultimo_error) / dt if dt > 0 else 0
        salida = self.Kp * error + self.Ki * self.integral + self.Kd * derivada
        self.ultimo_error = error
        return salida

    def mover_servo(self, angulo):
        angulo = max(self.servo_min, min(self.servo_max, angulo))
        if abs(angulo - self.last_servo_angle) >= 1:
            self.kit.servo[self.servo_channel].angle = angulo
            self.last_servo_angle = angulo

    def actualizar(self):
        angulo_actual, dt = self.get_angle_z()
        salida_pid = self.pid_control(angulo_actual, dt)
        angulo_servo = 90 + salida_pid
        self.mover_servo(angulo_servo)
        return angulo_actual, angulo_servo

    def adelante(self, velocidad=99, tiempo=1):
        self.reset_yaw()
        self.esc.angle = velocidad
        start = time.time()
        while time.time() - start < tiempo:
            self.actualizar()
            time.sleep(0.05)
        self.parar()
    
   

    def girar_izquierda(self, tiempo_giro=1, velocidad=105, servo_angulo=114):
        self.esc.angle = velocidad
        self.kit.servo[self.servo_channel].angle = servo_angulo
        time.sleep(tiempo_giro)
        self.kit.servo[self.servo_channel].angle = 90
        self.parar()

    def girar_derecha(self, tiempo_giro=1, velocidad=103, servo_angulo=65):
        self.esc.angle = velocidad
        self.kit.servo[self.servo_channel].angle = servo_angulo
        time.sleep(tiempo_giro)
        self.kit.servo[self.servo_channel].angle = 90
        self.parar()

    def parar(self):
        self.esc.angle = self.neutro
        self.kit.servo[self.servo_channel].angle = 90
"""
# Ejemplo de uso
steering = GyroSteering()
steering.adelante(tiempo=1.5)       
steering.girar_izquierda(tiempo_giro=1.2)

steering.adelante(tiempo=2)       
steering.girar_izquierda(tiempo_giro=1.2)

steering.adelante(tiempo=1.5)       
steering.girar_izquierda(tiempo_giro=1.2)

steering.adelante(tiempo=1)       
steering.girar_izquierda(tiempo_giro=1.2)
      # Avanza recto 2 segundos
"""
steering = GyroSteering()
VUELTAS = 3
num_vueltas = 0
try:
    while num_vueltas < VUELTAS * 4:
        distancias, variaciones = ultrasonido.obtener_distancias()

        dist_izq = distancias.get("izq", 100)
        dist_der = distancias.get("der", 100)
        dist_cen = distancias.get("cen", 100)


        # Deteccion de esquina (vacio lateral)
        if dist_der > DISTANCIA_VACIO:
             steering.girar_derecha(tiempo_giro=1.2)
             num_vueltas += 1# Vuelve al centro

        elif dist_izq > DISTANCIA_VACIO:
            steering.girar_izquierda(tiempo_giro=1.2)
            num_vueltas += 1

        # Obstaculo al frente
        
        # Correccion lateral (seguir linea recta)
        else:
            steering.adelante()
        #time.sleep(0.2)
        steering.parar()

except KeyboardInterrupt:
    steering.parar()
    print("Programa terminado por el usuario.")

finally:
    GPIO.cleanup()