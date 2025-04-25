import time
from src.classes.Config import Config
from simple_pid import PID

class PIDController:
    def __init__(self, setpoint, Kp=160, Ki=80, Kd=4):
        self.setpoint = setpoint
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.last_error = 0
        self.integral = 0
        self.last_time = time.time()
        self.config = Config()
        self.max_time_on = self.config.get_power_value('MAX_TIME_ON')
        self.pid = PID(Kp, Ki, Kd, setpoint=setpoint) 
        self.pid.output_limits = (0, self.max_time_on)

    def compute_power(self, current_temperature):
        """
        Oblicza wartość mocy na podstawie aktualnej temperatury.

        :param current_temperature: Aktualna temperatura pieca (°C)
        :return: Wartość mocy (0-1000)
        """
        return self.pid(current_temperature)
 