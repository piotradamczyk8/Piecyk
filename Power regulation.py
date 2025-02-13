import lgpio
import time
import tkinter as tk
from PZEM_004T import PZEM_004T
from Thermocouple import Thermocouple
import board
import busio
import adafruit_sht31d

# Konfiguracja pinów
ZERO_CROSS_PIN = 23  # Pin do wykrywania przejścia przez zero
TRIAC_PIN = 24       # Pin sterujący optotriakiem
FREQ = 50            # Częstotliwość sieci w Hz (np. 50Hz)
HALF_CYCLE = (1 / FREQ) / 2  # Połówka okresu
POWER = 1
DELAY = HALF_CYCLE

root = tk.Tk()
permision = 1
off_delay = 0
on_delay = 0
voltage_var = tk.DoubleVar(value="0.0")
current_var = tk.DoubleVar(value="0.0")
power_var = tk.DoubleVar(value="0.0")
energy_var = tk.DoubleVar(value="0.0")
freq_var = tk.DoubleVar(value="0.0")
cycle_var = tk.DoubleVar(value="0.0")
temperature = tk.DoubleVar(value="0.0")
bottom_cover_temperature = tk.DoubleVar(value="0.0")
humidity = tk.DoubleVar(value="0.0")
currentTime = tk.DoubleVar(value="0.0")


# Ustawienia GPIO
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
    root.geometry("640x640")
    root.title("Sterowanie Piecykiem")
    
    def set_impulses():
        global off_delay, on_delay
        off_delay = float(spinbox_impulse_prev.get())
        on_delay = float(spinbox_impulse_after.get())

    def clear_inputs():
        spinbox_impulse_prev.delete(0, 'end')
        spinbox_impulse_prev.insert(0, '0')
        spinbox_impulse_after.delete(0, 'end')
        spinbox_impulse_after.insert(0, '0')

    def set_inputs():
        global off_delay, on_delay
        off_delay = float(spinbox_impulse_prev.get())
        on_delay = float(spinbox_impulse_after.get())

        
    # Pola do podawania danych
    frame = tk.Frame(root)
    frame.pack(pady=(10, 10))



    tk.Label(frame, text="Time:", anchor="center").grid(row=0, column=0, padx=(10, 10),  pady=(10, 10))
    tk.Label(frame, textvariable=currentTime, anchor="center").grid(row=0, column=1, padx=(10, 10),  pady=(10, 10))

    tk.Label(frame, text="Frequency:", anchor="center").grid(row=1, column=0, padx=(10, 10),  pady=(10, 10))
    tk.Label(frame, textvariable=freq_var, anchor="center").grid(row=1, column=1, padx=(10, 10),  pady=(10, 10))

    tk.Label(frame, text="Cycle:", anchor="center").grid(row=2, column=0, padx=(10, 10))
    tk.Label(frame, textvariable=cycle_var, anchor="center").grid(row=2, column=1, padx=(10, 10))

    tk.Label(frame, text="TRIAC OFF (ms):", anchor="center").grid(row=3, column=0, padx=(10, 10), pady=(10, 10))
    impulse_prev_var = tk.DoubleVar(value=0)
    spinbox_impulse_prev = tk.Spinbox(frame, from_=0, to=5000, increment=1, textvariable=impulse_prev_var, width=5)
    spinbox_impulse_prev.grid(row=3, column=1, padx=(10, 10), pady=(10, 10))

    tk.Label(frame, text="TRIAC ON (ms):", anchor="center").grid(row=4, column=0, padx=(10, 10), pady=(10, 10))
    impulse_after_var = tk.DoubleVar(value=0)
    spinbox_impulse_after = tk.Spinbox(frame, from_=0, to=5000, increment=1, textvariable=impulse_after_var, width=5)
    spinbox_impulse_after.grid(row=4, column=1, padx=(10, 10), pady=(10, 10))

    tk.Button(frame, text="CLEAR", command=clear_inputs, anchor="center").grid(row=4, column=2, padx=(10, 10), pady=(10, 10))
    tk.Button(frame, text="SET", command=set_inputs, anchor="center").grid(row=4, column=3, padx=(10, 10), pady=(10, 10))

    tk.Label(frame, text="Voltage:", anchor="center").grid(row=5, column=0, padx=(10, 10), pady=(10, 10))
    tk.Label(frame, textvariable=voltage_var, anchor="center").grid(row=5, column=1, padx=(10, 10), pady=(10, 10))
        
    tk.Label(frame, text="Current:", anchor="center").grid(row=6, column=0, padx=(10, 10), pady=(10, 10))
    tk.Label(frame, textvariable=current_var, anchor="center").grid(row=6, column=1, padx=(10, 10), pady=(10, 10))

    tk.Label(frame, text="Power:", anchor="center").grid(row=6, column=0, padx=(10, 10), pady=(10, 10))
    tk.Label(frame, textvariable=power_var, anchor="center").grid(row=6, column=1, padx=(10, 10), pady=(10, 10))

    tk.Label(frame, text="Energy:", anchor="center").grid(row=8, column=0, padx=(10, 10), pady=(10, 10))
    tk.Label(frame, textvariable=energy_var, anchor="center").grid(row=8, column=1, padx=(10, 10), pady=(10, 10))

    tk.Label(frame, text="Temperature:", anchor="center").grid(row=9, column=0, padx=(10, 10), pady=(10, 10))
    tk.Label(frame, textvariable=temperature, anchor="center").grid(row=9, column=1, padx=(10, 10), pady=(10, 10))    
    
    tk.Label(frame, text="Bottom Cover Temperature:", anchor="center").grid(row=10, column=0, padx=(10, 10), pady=(10, 10))
    tk.Label(frame, textvariable=bottom_cover_temperature, anchor="center").grid(row=10, column=1, padx=(10, 10), pady=(10, 10))    
    
    tk.Label(frame, text="Humidity:", anchor="center").grid(row=11, column=0, padx=(10, 10), pady=(10, 10))
    tk.Label(frame, textvariable=humidity, anchor="center").grid(row=11, column=1, padx=(10, 10), pady=(10, 10))        

    tk.Button(frame, text="FINISH", command=stop_program, anchor="center").grid(row=12, column=0, columnspan=4, padx=(10, 10), pady=(10, 10))    
   
   
# Funkcja do aktualizacji danych z PZEM-004T
def update_pzem_data(pzem):
    pzem.read_data()
    voltage_var.set(f"{pzem.get_voltage():.2f}V")
    current_var.set(f"{pzem.get_current():.2f}A")
    power_var.set(f"{pzem.get_power():.2f}W")
    energy_var.set(f"{pzem.get_energy():}Wh")
    freq_var.set(f"{pzem.get_frequency():.2f}Hz")
    cycle_var.set(f"{round(1000/float(pzem.get_frequency()), 2):.2f}ms")

def update_thermocouple_data(thermocouple):
    temperature.set(f"{thermocouple.read_max31855():.2f}°C")
    
def update_temp_and_humidity(i2c):    
    sensor = adafruit_sht31d.SHT31D(i2c)
    bottom_cover_temperature.set(f"{sensor.temperature:.2f}°C")
    humidity.set(f"{sensor.relative_humidity:.2f}%")
    
def update_time(start_time):
    elapsed_time = int(time.time() - start_time)
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    currentTime.set(f"{hours:02}:{minutes:02}:{seconds:02}")

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
            update_thermocouple_data(thermocouple)
            update_pzem_data(pzem)
            update_temp_and_humidity(i2c)
            update_time(start_time)
            current_time = time.time()

        root.update_idletasks()
        root.update()          
          
except KeyboardInterrupt:    
    triac_pin_set_zero()
    print("Zatrzymano program przerwaniem.")

