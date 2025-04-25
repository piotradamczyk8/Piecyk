import tkinter as tk
import time
import lgpio
import board
import busio
import adafruit_sht31d
from src.classes.Config import Config
from src.classes.TemperatureCurves import TemperatureCurves
from src.classes.TemperatureApproximator import TemperatureApproximator
from src.classes.gui.LEDIndicator import LEDIndicator
from src.classes.utils import time_to_seconds
from src.classes.devices.PZEM_004T import PZEM_004T
from src.classes.devices.Thermocouple import Thermocouple
from src.classes.devices.SSR import SSR
from src.classes.CSVLogger import CSVLogger

class GlobalState:
    def __init__(self, init_gui=False):
        """Inicjalizacja stanu globalnego.
        
        Args:
            init_gui (bool): Czy zainicjalizować GUI podczas tworzenia obiektu.
        """
        # Konfiguracja
        self.config = Config()
        
        # Stałe
        self.FREQ = self.config.get_power_value('FREQ')
        self.HALF_CYCLE = self.config.get_power_value('HALF_CYCLE')
        self.POWER = self.config.get_power_value('POWER')
        self.DELAY = self.config.get_power_value('DELAY')
        self.MAX_TIME_ON = self.config.get_power_value('MAX_TIME_ON')
        
        # Zmienne Tkinter (zainicjalizowane później)
        self.root = None
        self.curve_var = None
        self.progress_var = None
        self.impulse_prev_var = None
        self.impulse_after_var = None
        self.voltage_var = None
        self.current_var = None
        self.power_var = None
        self.energy_var = None
        self.freq_var = None
        self.cycle_var = None
        self.temperature_thermocouple_var = None
        self.bottom_cover_temperature = None
        self.humidity = None
        self.elapsed_time_var = None
        self.remaining_time_var = None
        self.final_time_var = None
        self.temperature_ir_var = None
        self.temperature_expected_var = None
        self.temperature_approximate_var = None
        self.progres_var_percent = None
        self.curve_description_var = None
        self.curve_description = None
        # Zmienne stanu
        self.temp_plot = None
        self.progress_bar = None
        self.temperature_schedule = {}
        self.permision = 1
        self.off_delay = 0
        self.on_delay = 0
        self.elapsed_time = 0
        self.remaining_time = 0
        self.add_time = time_to_seconds("00:00")
        self.start_time = time.time()
        self.current_time = self.start_time
        self.last_update_time = self.start_time
        
        # Obiekty
        self.temperature_curves = TemperatureCurves()
        self.temp_calc = TemperatureApproximator()
        self.led_indicator = None
        
        # Inicjalizacja urządzeń
        self.h = None
        self.pzem = PZEM_004T()
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.thermocouple = Thermocouple()
        self.ssr = SSR()
        
        # Inicjalizacja loggera CSV
        self.csv_logger = None
        
        # Zmienne dla obsługi sygnałów
        self.global_h = None
        self.global_ssr = None
        self.global_root = None
        self.global_file = None
        
        # Inicjalizacja dodatkowych wartości
        self.curves = self.temperature_curves.get_curves()
        self.description = self.temperature_curves.get_curve_stage("Bisquit", "01:36:02")
        
        # Inicjalizacja GUI jeśli wymagana
        if init_gui:
            self.init_gui()
        
    def init_gui(self):
        """Inicjalizuje GUI."""
        try:
            # Utwórz główne okno
            self.root = tk.Tk()
            self.root.geometry(f"{self.config.get_gui_value('WINDOW_WIDTH')}x{self.config.get_gui_value('WINDOW_HEIGHT')}")
            self.root.title("Kiln Control System")
            
            # Sprawdź, czy główne okno zostało utworzone
            if not self.root:
                raise RuntimeError("Nie udało się utworzyć głównego okna")
            
            # Inicjalizuj zmienne Tkinter
            self.curve_var = tk.StringVar(master=self.root, value=self.config.get_gui_value('DEFAULT_CURVE'))
            self.progress_var = tk.DoubleVar(master=self.root, value=0)
            self.impulse_prev_var = tk.DoubleVar(master=self.root, value=0)
            self.impulse_after_var = tk.DoubleVar(master=self.root, value=0)
            self.voltage_var = tk.DoubleVar(master=self.root, value="0.0")
            self.current_var = tk.DoubleVar(master=self.root, value="0.0")
            self.power_var = tk.DoubleVar(master=self.root, value="0.0")
            self.energy_var = tk.DoubleVar(master=self.root, value="0.0")
            self.freq_var = tk.DoubleVar(master=self.root, value="0.0")
            self.cycle_var = tk.DoubleVar(master=self.root, value="0.0")
            self.temperature_thermocouple_var = tk.DoubleVar(master=self.root, value="0.0")
            self.bottom_cover_temperature = tk.DoubleVar(master=self.root, value="0.0")
            self.humidity = tk.DoubleVar(master=self.root, value="0.0")
            self.elapsed_time_var = tk.StringVar(master=self.root, value="00:00:00")
            self.remaining_time_var = tk.StringVar(master=self.root, value="00:00:00")
            self.final_time_var = tk.StringVar(master=self.root, value="00:00")
            self.temperature_ir_var = tk.DoubleVar(master=self.root, value="0.0")
            self.temperature_expected_var = tk.DoubleVar(master=self.root, value="0.0")
            self.temperature_approximate_var = tk.DoubleVar(master=self.root, value="0.0")
            self.progres_var_percent = tk.StringVar(master=self.root, value="0")
            self.curve_description_var = tk.StringVar(master=self.root, value="")
            self.curve_description = tk.StringVar(master=self.root, value="")

            # Utwórz wskaźnik LED
            self.led_indicator = LEDIndicator(self.root)
        except Exception as e:
            print(f"Błąd przy inicjalizacji GUI: {e}")
            self.root = None
            self.led_indicator = None
        
    def get_all_vars(self):
        """Zwraca słownik ze wszystkimi zmiennymi Tkinter."""
        if not self.root:
            raise RuntimeError("GUI nie zostało zainicjalizowane")
            
        return {
            'curve_var': self.curve_var,
            'progress_var': self.progress_var,
            'impulse_prev_var': self.impulse_prev_var,
            'impulse_after_var': self.impulse_after_var,
            'voltage_var': self.voltage_var,
            'current_var': self.current_var,
            'power_var': self.power_var,
            'energy_var': self.energy_var,
            'freq_var': self.freq_var,
            'cycle_var': self.cycle_var,
            'temperature_thermocouple_var': self.temperature_thermocouple_var,
            'bottom_cover_temperature': self.bottom_cover_temperature,
            'humidity': self.humidity,
            'elapsed_time_var': self.elapsed_time_var,
            'remaining_time_var': self.remaining_time_var,
            'final_time_var': self.final_time_var,
            'temperature_ir_var': self.temperature_ir_var,
            'temperature_expected_var': self.temperature_expected_var,
            'temperature_approximate_var': self.temperature_approximate_var,
            'progres_var_percent': self.progres_var_percent,
            'curve_description_var': self.curve_description_var,
            'curve_description': self.curve_description
        }
        
    def update_time(self):
        """Aktualizuje czas w stanie."""
        self.elapsed_time = time.time() - self.start_time
        self.current_time = time.time()
        
        # Pobierz wartości ze zmiennych Tkinter
        curve_name = self.curve_var.get() if self.curve_var else ""
        elapsed_time_str = self.elapsed_time_var.get() if self.elapsed_time_var else "00:00:00"
        
        # Pobierz opis krzywej
        curve_desc = self.temperature_curves.get_curve_stage(curve_name, elapsed_time_str)
        
        # Ustaw opis krzywej w zmiennej Tkinter
        if self.curve_description_var:
            self.curve_description_var.set(curve_desc)
        
    def reset_time(self):
        """Resetuje czas w stanie."""
        self.start_time = time.time()
        self.current_time = self.start_time
        self.elapsed_time = 0
        
    def setup_gpio(self):
        """Inicjalizuje GPIO."""
        try:
            self.h = lgpio.gpiochip_open(0)
            return self.h
        except Exception as e:
            print(f"Błąd przy otwieraniu GPIO: {e}")
            return None
            
    def setup_csv_logger(self):
        """Inicjalizuje logger CSV."""
        if not self.root:
            raise RuntimeError("GUI nie zostało zainicjalizowane")
        self.csv_logger = CSVLogger(self.curve_var.get(), self.config)
        
    def cleanup(self):
        """Zamyka wszystkie zasoby."""
        if self.csv_logger:
            self.csv_logger.close()
        if self.h:
            lgpio.gpiochip_close(self.h)
        if self.ssr:
            del self.ssr
        if self.root:
            self.root.quit()
            self.root.destroy() 