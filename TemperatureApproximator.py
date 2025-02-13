class TemperatureApproximator:
    def __init__(self):
        self.temperature_ir_var = None  # Ostatnia wartość IR
        self.temperature_offset = 0  # Różnica między IR a termoparą
        self.temperature_approximate_var = None  # Przybliżona temperatura

    def update_ir_temperature(self, temperature_ir_var, temperature_thermocouple_var):
        """Aktualizuje temperaturę IR, przelicza offset i resetuje przybliżoną temperaturę."""
        self.temperature_ir_var = temperature_ir_var
        self.temperature_offset = self.temperature_ir_var - temperature_thermocouple_var
        self.temperature_approximate_var = self.temperature_ir_var  # IR jest prawidłową temperaturą

    def update_thermocouple_temperature(self, temperature_thermocouple_var):
        """Aktualizuje temperaturę termopary i oblicza przybliżoną wartość."""
        if self.temperature_ir_var is not None:
            self.temperature_approximate_var = temperature_thermocouple_var + self.temperature_offset
        else:
            self.temperature_approximate_var = temperature_thermocouple_var  # Gdy nie mamy IR, używamy termopary

    def get_approximate_temperature(self):
        """Zwraca aktualną przybliżoną temperaturę."""
        return self.temperature_approximate_var
