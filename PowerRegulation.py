import lgpio
import time
import tkinter as tk
from PZEM_004T import PZEM_004T
from Thermocouple import Thermocouple
from TemperatureApproximator import TemperatureApproximator
import board
import busio
import adafruit_sht31d
import csv
import numpy as np
from PIDController import PIDController

##############################################
# Stałe
##############################################
ZERO_CROSS_PIN = 23  # Pin do wykrywania przejścia przez zero
TRIAC_PIN = 24       # Pin sterujący optotriakiem
FREQ = 50            # Częstotliwość sieci w Hz (np. 50Hz)
HALF_CYCLE = (1 / FREQ) / 2  # Połówka okresu
POWER = 1
DELAY = HALF_CYCLE

def time_to_seconds(time_str):
    """Convert time in hh:mm format to seconds."""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 3600 + minutes * 60

def seconds_to_time(seconds):
    """Convert seconds to time in hh:mm format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02}:{minutes:02}"

##############################################
# Zmienne globalne
##############################################
root = tk.Tk()
permision = 1
off_delay = 0
on_delay = 0
impulse_prev_var = tk.DoubleVar(value=0)
spinbox_impulse_prev = tk.Spinbox(root, from_=0, to=5000, increment=1, textvariable=impulse_prev_var, width=5)
impulse_after_var = tk.DoubleVar(value=0)
spinbox_impulse_after = tk.Spinbox(root, from_=0, to=5000, increment=1, textvariable=impulse_after_var, width=5)
voltage_var = tk.DoubleVar(value="0.0")
current_var = tk.DoubleVar(value="0.0")
power_var = tk.DoubleVar(value="0.0")
energy_var = tk.DoubleVar(value="0.0")
freq_var = tk.DoubleVar(value="0.0")
cycle_var = tk.DoubleVar(value="0.0")
temperature_thermocouple_var = tk.DoubleVar(value="0.0")
bottom_cover_temperature = tk.DoubleVar(value="0.0")
humidity = tk.DoubleVar(value="0.0")
elapsed_time_var = tk.StringVar(value="00:00:00")
remaining_time_var = tk.StringVar(value="00:00:00")
temperature_ir_var = tk.DoubleVar(value="0.0")
temperature_expected_var = tk.DoubleVar(value="0.0")
temperature_approximate_var = tk.DoubleVar(value="0.0")

elapsed_time = 0
add_time = time_to_seconds("06:30") # Dodatkowy czas w minutach

bisquit_curve = {
        0: 30,
        3: 200,
        4: 400,
        5: 500,
        6: 600,
        7: 800,
        8: 950,
        9: 1050
    }

glazing_curve = {
        0: 30,
        2: 200,
        3: 850,
        4: 950,
        5: 1050
    }

temp_calc = TemperatureApproximator()

##############################################
# Funkcje pomocnicze
##############################################

def setup_gpio():
    global h
    h = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_input(h, ZERO_CROSS_PIN)
    lgpio.gpio_claim_output(h, TRIAC_PIN)
    lgpio.gpio_write(h, TRIAC_PIN, 0)

def stop_program():
    triac_pin_set_zero()
    lgpio.gpiochip_close(h)
    print("Zatrzymano program przyciskiem")
    exit(0)

def triac_pin_set_zero():
    lgpio.gpio_claim_output(h, TRIAC_PIN)
    lgpio.gpio_write(h, TRIAC_PIN, 0)  

def regulation_desk():        
    root.geometry("640x780")
    root.title("Sterowanie Piecykiem")

def clear_inputs():
    global off_delay, on_delay
    spinbox_impulse_prev.delete(0, 'end')
    spinbox_impulse_prev.insert(0, '0')
    spinbox_impulse_after.delete(0, 'end')
    spinbox_impulse_after.insert(0, '0')
    off_delay = 0
    on_delay = 0

def set_inputs():
    global off_delay, on_delay
    off_delay = float(spinbox_impulse_prev.get())
    on_delay = float(spinbox_impulse_after.get())

def set_temperature_ir():
    temperature_ir_var.set(float(spinbox_temperature_ir_var.get()))
    temp_calc.update_ir_temperature(float(spinbox_temperature_ir_var.get()), float(temperature_thermocouple_var.get()))
     
# Funkcja do aktualizacji danych z PZEM-004T
def update_pzem_data(pzem):
    pzem.read_data()
    voltage_var.set(f"{pzem.get_voltage():.2f}")
    current_var.set(f"{pzem.get_current():.2f}")
    power_var.set(f"{pzem.get_power():.2f}")
    energy_var.set(f"{pzem.get_energy():}")
    freq_var.set(f"{pzem.get_frequency():.2f}")
    cycle_var.set(f"{round(1000/float(pzem.get_frequency()), 2):.2f}")

def update_temperature(thermocouple):
    temp_calc.update_thermocouple_temperature(thermocouple.read_max31855()) 
    temperature_thermocouple_var.set(f"{thermocouple.read_max31855():.2f}")    
    temperature_approximate_var.set(temp_calc.get_approximate_temperature())
    
def update_temp_and_humidity(i2c):    
    sensor = adafruit_sht31d.SHT31D(i2c)
    bottom_cover_temperature.set(f"{sensor.temperature:.2f}")
    humidity.set(f"{sensor.relative_humidity:.2f}")
    
def update_time():
    hours, remainder = divmod(int(elapsed_time), 3600)
    minutes, seconds = divmod(remainder, 60)
    elapsed_time_var.set(f"{hours:02}:{minutes:02}:{seconds:02}")
    
    remaining_time = max(temperature_schedule.keys()) * 3600 - elapsed_time
    hours, remainder = divmod(int(remaining_time), 3600)
    minutes, seconds = divmod(remainder, 60)
    remaining_time_var.set(f"{hours:02}:{minutes:02}:{seconds:02}") 
    

def update_PID():
    global elapsed_time, on_delay, impulse_after_var
    pid = PIDController(setpoint=800, Kp=2.0, Ki=0.1, Kd=0.05)
    on_delay = int(pid.compute_power(temperature_approximate_var.get())) #czas w ms do sterowania triakiem
    impulse_after_var.set(on_delay)

def get_expected_temperature() -> float:
    global temperature_schedule
    
    # Konwersja godzin na sekundy
    schedule_seconds = {k * 3600: v for k, v in temperature_schedule.items()}
    
    times = sorted(schedule_seconds.keys())
    temps = [schedule_seconds[t] for t in times]
    
    # Jeśli elapsed_time jest poza zakresem, zwracamy graniczne wartości
    if elapsed_time <= times[0]:
        return temps[0]
    elif elapsed_time >= times[-1]:
        return temps[-1]
    
    # Znajdujemy przedział, w którym znajduje się elapsed_time
    for i in range(len(times) - 1):
        if times[i] <= elapsed_time <= times[i + 1]:
            # Interpolacja liniowa
            t1, t2 = times[i], times[i + 1]
            temp1, temp2 = temps[i], temps[i + 1]
            
            temperature = temp1 + (temp2 - temp1) * (elapsed_time - t1) / (t2 - t1)
            return temperature
    
    return None  # Wartość ta nie powinna nigdy zostać zwrócona

def write_data(file_handle):
    global spinbox_impulse_prev, spinbox_impulse_after

    data = [{"elapsed_time_var": str(elapsed_time_var.get()), 
            "Triac off": str(spinbox_impulse_prev.get()),
            "Triac on": str(spinbox_impulse_after.get()),
            "temperature thermocouple": str(temperature_thermocouple_var.get()),
            "temperature_ir": temperature_ir_var.get(),
            "temperature_approximate": str(temperature_approximate_var.get()),
            "temperature_expected": str(temperature_expected_var.get()),
            "bottom_cover_temperature": f"{bottom_cover_temperature.get()}",
            "humidity": f"{humidity.get()}",
            "voltage": f"{voltage_var.get()}",
            "current": f"{current_var.get()}",
            "power": f"{power_var.get()}",
            "energy": f"{energy_var.get()}",
            "freq": f"{freq_var.get()}",
            "cycle": f"{cycle_var.get()}"
            }]

    fieldnames = [
        "elapsed_time_var", 
        "Triac off", 
        "Triac on", 
        "temperature thermocouple",
        "temperature_ir",
        "temperature_approximate",
        "temperature_expected",
        "bottom_cover_temperature",
        "humidity",
        "voltage",
        "current",
        "power",
        "energy",
        "freq",
        "cycle"
    ]

    writer = csv.DictWriter(file_handle, fieldnames=fieldnames)

    # Jeśli plik jest nowy i pusty, dodaj nagłówek (sprawdzamy czy kursor jest na początku)
    if file_handle.tell() == 0:
        writer.writeheader()

    writer.writerows(data)  # Zapisanie danych

############################################
    # GUI
############################################

frame = tk.Frame(root)
frame.pack(pady=(10, 10))

# Dodanie pola wyboru dla krzywej wypału
curve_var = tk.StringVar(value="bisquit_curve")

temperature_schedule = bisquit_curve #defaultowo wybrana krzywa bisquit_curve

def set_temperature_schedule(selected_curve):
    global temperature_schedule
    selected_curve = curve_var.get()
    if selected_curve == "bisquit_curve":
        temperature_schedule = bisquit_curve
    elif selected_curve == "glazing_curve":
        temperature_schedule = glazing_curve

curve_var = tk.StringVar(value="bisquit_curve")
curve_option_menu = tk.OptionMenu(frame, curve_var, "bisquit_curve", "glazing_curve", command=set_temperature_schedule)
curve_option_menu.config(width=15)
curve_option_menu.grid(row=0, column=0, columnspan=3, padx=(10, 10), pady=(10, 10))

tk.Label(frame, text="Elapsed Time:", anchor="center").grid(row=1, column=0, padx=(10, 10),  pady=(10, 10))
tk.Label(frame, textvariable=elapsed_time_var, anchor="center").grid(row=1, column=1, padx=(10, 10),  pady=(10, 10))

tk.Label(frame, text="Remaining Time:", anchor="center").grid(row=2, column=0, padx=(10, 10),  pady=(10, 10))
tk.Label(frame, textvariable=remaining_time_var, anchor="center").grid(row=2, column=1, padx=(10, 10),  pady=(10, 10))

tk.Label(frame, text="Frequency (Hz):", anchor="center").grid(row=3, column=0, padx=(10, 10),  pady=(10, 10))
tk.Label(frame, textvariable=freq_var, anchor="center").grid(row=3, column=1, padx=(10, 10),  pady=(10, 10))

tk.Label(frame, text="Cycle (ms):", anchor="center").grid(row=4, column=0, padx=(10, 10))
tk.Label(frame, textvariable=cycle_var, anchor="center").grid(row=4, column=1, padx=(10, 10))

tk.Label(frame, text="Triac on (ms):", anchor="center").grid(row=5, column=0, padx=(10, 10), pady=(10, 10))
tk.Label(frame, textvariable=impulse_after_var, anchor="center").grid(row=5, column=1, padx=(10, 10))

tk.Label(frame, text="Voltage (V):", anchor="center").grid(row=6, column=0, padx=(10, 10), pady=(10, 10))
tk.Label(frame, textvariable=voltage_var, anchor="center").grid(row=6, column=1, padx=(10, 10), pady=(10, 10))
    
tk.Label(frame, text="Current (A):", anchor="center").grid(row=7, column=0, padx=(10, 10), pady=(10, 10))
tk.Label(frame, textvariable=current_var, anchor="center").grid(row=7, column=1, padx=(10, 10), pady=(10, 10))

tk.Label(frame, text="Power (W):", anchor="center").grid(row=8, column=0, padx=(10, 10), pady=(10, 10))
tk.Label(frame, textvariable=power_var, anchor="center").grid(row=8, column=1, padx=(10, 10), pady=(10, 10))

tk.Label(frame, text="Energy (Wh):", anchor="center").grid(row=9, column=0, padx=(10, 10), pady=(10, 10))
tk.Label(frame, textvariable=energy_var, anchor="center").grid(row=9, column=1, padx=(10, 10), pady=(10, 10))

tk.Label(frame, text="Thermocouple temperature (°C):", anchor="center").grid(row=10, column=0, padx=(10, 10), pady=(10, 10))
tk.Label(frame, textvariable=temperature_thermocouple_var, anchor="center").grid(row=10, column=1, padx=(10, 10), pady=(10, 10))   

tk.Label(frame, text="Temperature IR (°C):", anchor="center").grid(row=11, column=0, padx=(10, 10), pady=(10, 10))
temperature_ir_var = tk.DoubleVar(value=0)
spinbox_temperature_ir_var = tk.Spinbox(frame, from_=-1000, to=1000, increment=1, textvariable=temperature_ir_var, width=5)
spinbox_temperature_ir_var.grid(row=11, column=1, padx=(10, 10), pady=(10, 10)) 
tk.Button(frame, text="SET", command=set_temperature_ir, anchor="center").grid(row=11, column=2, padx=(10, 10), pady=(10, 10))

tk.Label(frame, text="Temperature approximate (°C):", anchor="center").grid(row=12, column=0, padx=(10, 10), pady=(10, 10))
tk.Label(frame, textvariable=temperature_approximate_var, anchor="center").grid(row=12, column=1, padx=(10, 10), pady=(10, 10))    

tk.Label(frame, text="Temperature expected (°C):", anchor="center").grid(row=13, column=0, padx=(10, 10), pady=(10, 10))
tk.Label(frame, textvariable=temperature_expected_var, anchor="center").grid(row=13, column=1, padx=(10, 10), pady=(10, 10))    

tk.Label(frame, text="Bottom Cover Temperature (°C):", anchor="center").grid(row=14, column=0, padx=(10, 10), pady=(10, 10))
tk.Label(frame, textvariable=bottom_cover_temperature, anchor="center").grid(row=14, column=1, padx=(10, 10), pady=(10, 10))    

tk.Label(frame, text="Humidity (%):", anchor="center").grid(row=15, column=0, padx=(10, 10), pady=(10, 10))
tk.Label(frame, textvariable=humidity, anchor="center").grid(row=15, column=1, padx=(10, 10), pady=(10, 10))        

tk.Button(frame, text="FINISH", command=stop_program, anchor="center").grid(row=16, column=0, columnspan=4, padx=(10, 10), pady=(10, 10))


#############################
# PROGRAM GŁÓWNY
#############################

# Inicjalizacja GPIO
setup_gpio()

# Inicjalizacja PZEM-004T
pzem = PZEM_004T()

# Inicjalizacja I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicjalizacja termopary
thermocouple = Thermocouple()

# Inicjalizacja GUI
regulation_desk()

# Utworzenie pliku CSV
file = open("dane_biskwit_2025-02-13.csv", mode="a", newline="", encoding="utf-8")
writer = csv.writer(file)

try:
    # Główna pętla programu
    start_time = time.time()
    current_time = start_time
    while True:
        
        #Przejście przez zero
        if lgpio.gpio_read(h, ZERO_CROSS_PIN) == 0 and permision == 1:
            # Włączenie optotriaka
            lgpio.gpio_write(h, TRIAC_PIN, 1)
            time.sleep(on_delay/1000)            

            # Wyłączenie optotriaka
            lgpio.gpio_write(h, TRIAC_PIN, 0)    
            time.sleep(off_delay/1000)
            permision = 0

        if lgpio.gpio_read(h, ZERO_CROSS_PIN) == 1:
            permision = 1

        # Aktualizacja wskazań miernika PZEM-004T co 1 sekundę
        if time.time() - current_time >= 1:            
            elapsed_time = time.time() - start_time + add_time            
            update_temperature(thermocouple)
            update_pzem_data(pzem)
            update_temp_and_humidity(i2c)
            update_time()
            write_data(file)
            current_time = time.time()
            temperature_expected_var.set(f"{get_expected_temperature():.2f}")
            update_PID()

        root.update_idletasks()
        root.update()          
          
except KeyboardInterrupt:    
    triac_pin_set_zero()
    print("Zatrzymano program przerwaniem.")
finally:
    file.close()