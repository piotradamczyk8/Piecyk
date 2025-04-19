from simple_pid import PID

class PIDController:
    def __init__(self, setpoint=800, kp=2.0, ki=0.1, kd=0.05, min_output=0, max_output=10000):
        """
        Inicjalizuje regulator PID.

        :param setpoint: Docelowa temperatura pieca (°C)
        :param kp: Wzmocnienie proporcjonalne
        :param ki: Wzmocnienie całkowe
        :param kd: Wzmocnienie różniczkowe
        :param min_output: Minimalna wartość wyjściowa
        :param max_output: Maksymalna wartość wyjściowa
        """
        self.pid = PID(kp, ki, kd, setpoint=setpoint) 
        self.pid.output_limits = (min_output, max_output)

    
    def set_target_temperature(self, temperature):
        """
        Ustawia nową temperaturę oczekiwaną.

        :param temperature: Nowa wartość temperatury (°C)
        """
        self.pid.setpoint = temperature

    def compute_power(self, current_temperature):
        """
        Oblicza wartość mocy na podstawie aktualnej temperatury.

        :param current_temperature: Aktualna temperatura pieca (°C)
        :return: Wartość mocy (0-1000)
        """
        return self.pid(current_temperature)
