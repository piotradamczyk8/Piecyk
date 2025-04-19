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
    baudrate=config.getint("PZEM", "baudrate")
)

# Inicjalizacja termopary
thermocouple = Thermocouple()

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

# Inicjalizacja aplikacji
app = Application()

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
final_time = 0

# Zmienne temperatury
temperature_thermocouple = 0.0
temperature_approximate = 0.0
temperature_expected = 0.0

# Zmienne PZEM
voltage = 0.0
current = 0.0
power = 0.0
energy = 0.0
cycle = 0
impulse_after = 0

def update_time():
    global elapsed_time, start_time
    if start_time > 0:
        elapsed_time = time.time() - start_time + add_time
    return elapsed_time

def update_data():
    global elapsed_time, remaining_time, final_time, cycle, impulse_after, voltage, current, power, energy
    global temperature_thermocouple, temperature_approximate, temperature_expected
    global current_cycle
    
    # Pobierz aktualny etap
    current_stage = temperature_curves.get_current_stage(elapsed_time)
    
    # Oblicz final_time na podstawie aktualnej krzywej
    selected_curve = temperature_curves.get_selected_curve()
    if selected_curve:
        curve_data = temperature_curves.get_curve(selected_curve)
        if curve_data:
            final_time = curve_data[-1][0]  # Ostatni punkt czasowy w krzywej
    
    # Aktualizuj dane w InfoFrame
    app.get_info_frame().update_data({
        "Current Stage": current_stage,
        "Time": f"{elapsed_time:.0f}/{final_time:.0f}",
        "Temperature": f"{temperature_thermocouple:.1f}°C",
        "Power": f"{power:.1f}W",
        "Energy": f"{energy:.1f}Wh",
        "Cycles": cycle
    })
    
    while is_running:
        # Aktualizacja czasu
        current_time = update_time()
        
        # Odczyt temperatury z termopary
        thermocouple_temp = thermocouple.read_max31855()
        temperature_approximator.update_thermocouple_temperature(thermocouple_temp)
        approximate_temp = temperature_approximator.get_approximate_temperature()
        
        # Pobranie oczekiwanej temperatury z krzywej
        expected_temp = temperature_curves.get_expected_temperature(current_time)
        
        # Obliczenie mocy z PID
        power = pid.compute_power(approximate_temp)
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