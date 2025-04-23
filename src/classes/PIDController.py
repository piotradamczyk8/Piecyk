import time
from src.classes.Config import Config

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

    def compute_power(self, current_value):
        """Oblicza moc wyjściową na podstawie wartości aktualnej i zadanej."""
        current_time = time.time()
        dt = current_time - self.last_time

        error = self.setpoint - current_value
        self.integral += error * dt
        derivative = (error - self.last_error) / dt if dt > 0 else 0

        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # Ograniczenie wyjścia do zakresu 0-100%
        output = max(0, min(100, output))

        # Konwersja procentu na czas włączenia w milisekundach
        time_on = (output / 100) * self.max_time_on

        self.last_error = error
        self.last_time = current_time

        return time_on
 