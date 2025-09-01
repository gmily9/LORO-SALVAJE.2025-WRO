from mpu6050 import mpu6050
from adafruit_servokit import ServoKit
import time

class GyroSteering:
    def _init_(self, servo_channel=0, Kp=0.6, Ki=0.0, Kd=0.1, servo_min=60, servo_max=120):
        self.sensor = mpu6050(0x68)
        self.kit = ServoKit(channels=16)

        self.servo_channel = servo_channel
        self.servo_min = servo_min
        self.servo_max = servo_max

        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.integral = 0.0
        self.ultimo_error = 0.0
        self.angulo_deseado = 0.0
        self.angle_z = 0.0
        self.last_time = time.time()
        self.last_servo_angle = 90

    def get_angle_z(self):
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        gyro_data = self.sensor.get_gyro_data()
        gyro_z = gyro_data['z']

        self.angle_z += gyro_z * dt
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