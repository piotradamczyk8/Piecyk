from simple_pid import PID

class PIDController:
    def __init__(self, setpoint=800, Kp=2.0, Ki=0.1, Kd=0.05):
        """
        Inicjalizuje regulator PID.

        :param setpoint: Docelowa temperatura pieca (°C)
        :param Kp: Wzmocnienie proporcjonalne
        :param Ki: Wzmocnienie całkowe
        :param Kd: Wzmocnienie różniczkowe
        """
        self.pid = PID(Kp, Ki, Kd, setpoint=setpoint) 
        self.pid.output_limits = (0, 500)

    
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
