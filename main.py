import lgpio
import time
import csv
from datetime import datetime
from src.gui.Application import Application
from src.classes.PZEM_004T import PZEM_004T
from src.classes.Thermocouple import Thermocouple
from src.classes.TemperatureApproximator import TemperatureApproximator
from src.classes.PIDController import PIDController
from src.classes.TemperatureCurves import TemperatureCurves
from src.gui.frames.InfoFrame import InfoFrame
from src.classes.Config import Config

# Inicjalizacja konfiguracji
config = Config()

# Inicjalizacja GPIO
h = lgpio.gpiochip_open(config.getint("GPIO", "gpio_chip"))
TRIAC_PIN = config.getint("GPIO", "triac_pin")
lgpio.gpio_claim_output(h, TRIAC_PIN)
lgpio.gpio_write(h, TRIAC_PIN, 0)

# Inicjalizacja PZEM
pzem = PZEM_004T(
    port=config.get("PZEM", "port"),
    baudrate=config.getint("PZEM", "baudrate"),
    address=config.getint("PZEM", "address")
)

# Inicjalizacja termopary
thermocouple = Thermocouple(
    cs_pin=config.getint("Thermocouple", "cs_pin"),
    clock_pin=config.getint("Thermocouple", "clock_pin"),
    data_pin=config.getint("Thermocouple", "data_pin"),
    max_temperature=config.getfloat("Thermocouple", "max_temperature"),
    min_temperature=config.getfloat("Thermocouple", "min_temperature")
)

temperature_approximator = TemperatureApproximator()

# Inicjalizacja PID
pid = PIDController(
    kp=config.getfloat("PID", "kp"),
    ki=config.getfloat("PID", "ki"),
    kd=config.getfloat("PID", "kd"),
    min_output=config.getfloat("PID", "min_output"),
    max_output=config.getfloat("PID", "max_output")
)

# Inicjalizacja krzywych temperatury
temperature_curves = TemperatureCurves(curves_dir=config.get("Files", "curves_dir"))

# Inicjalizacja InfoFrame
info_frame = InfoFrame()

# Inicjalizacja pliku CSV
csv_file = open(config.get("Files", "data_file"), 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Time', 'Thermocouple', 'Approximate', 'Expected', 'Power'])

# Zmienne globalne
elapsed_time = 0
add_time = 0
start_time = 0
current_power = 0
current_cycle = 0
max_cycles = config.getint("Control", "max_cycles")
is_running = True

def update_time():
    global elapsed_time, start_time
    if start_time > 0:
        elapsed_time = time.time() - start_time + add_time
    return elapsed_time

def update_data():
    global elapsed_time, remaining_time, final_time, cycle, impulse_after, voltage, current, power, energy
    global temperature_thermocouple, temperature_approximate, temperature_expected
    
    # Pobierz aktualny etap
    current_stage = temperature_curves.get_current_stage(elapsed_time)
    
    # Aktualizuj dane w InfoFrame
    info_frame.update_data({
        "Current Stage": current_stage,
        "Time": f"{elapsed_time}/{final_time}",
        "Temperature": f"{temperature_thermocouple:.1f}°C",
        "Power": f"{power:.1f}W",
        "Energy": f"{energy:.1f}Wh",
        "Cycles": cycle
    })
    
    while is_running:
        # Aktualizacja czasu
        current_time = update_time()
        
        # Odczyt temperatury z termopary
        thermocouple_temp = thermocouple.read_temperature()
        temperature_approximator.update(thermocouple_temp)
        approximate_temp = temperature_approximator.get_temperature()
        
        # Pobranie oczekiwanej temperatury z krzywej
        expected_temp = temperature_curves.get_expected_temperature(current_time)
        
        # Obliczenie mocy z PID
        power = pid.compute(approximate_temp, expected_temp)
        current_power = max(0, min(config.getfloat("Control", "max_power"), power))
        
        # Aktualizacja triaka
        if current_cycle < max_cycles:
            if current_cycle < (current_power / 100.0) * max_cycles:
                lgpio.gpio_write(h, TRIAC_PIN, 1)
            else:
                lgpio.gpio_write(h, TRIAC_PIN, 0)
            current_cycle = (current_cycle + 1) % max_cycles
        
        # Zapis danych do CSV
        csv_writer.writerow([
            datetime.now().strftime('%H:%M:%S'),
            f"{thermocouple_temp:.1f}",
            f"{approximate_temp:.1f}",
            f"{expected_temp:.1f}",
            f"{current_power:.1f}"
        ])
        csv_file.flush()
        
        time.sleep(config.getfloat("Control", "update_interval"))

def stop_program():
    """Bezpieczne zakończenie programu"""
    global is_running
    is_running = False
    
    try:
        # Wyłącz triak
        lgpio.gpio_write(h, TRIAC_PIN, 0)
        
        # Zamknij plik CSV
        if 'csv_file' in globals() and csv_file:
            csv_file.close()
            print("Zamknięto plik CSV")
            
        # Zamknij połączenie GPIO
        if 'h' in globals() and h:
            lgpio.gpiochip_close(h)
            print("Zamknięto połączenie GPIO")
            
        print("Program zakończony pomyślnie")
        
    except Exception as e:
        print(f"Błąd przy zamykaniu programu: {e}")

def main():
    # Inicjalizacja aplikacji
    app = Application(
        title=config.get("GUI", "window_title"),
        width=config.getint("GUI", "window_width"),
        height=config.getint("GUI", "window_height")
    )
    
    # Uruchomienie wątku aktualizacji danych
    import threading
    data_thread = threading.Thread(target=update_data)
    data_thread.daemon = True
    data_thread.start()
    
    # Uruchomienie aplikacji
    app.run()
    
    # Zamknięcie programu
    stop_program()

if __name__ == "__main__":
    main() 