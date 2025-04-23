import lgpio
import time
import tkinter as tk
from tkinter import ttk
import board
import busio
import adafruit_sht31d
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import signal
import sys
import os

from src.classes.devices.PZEM_004T import PZEM_004T
from src.classes.devices.Thermocouple import Thermocouple
from src.classes.TemperatureApproximator import TemperatureApproximator
from src.classes.PIDController import PIDController
from src.classes.TemperatureCurves import TemperatureCurves
from src.classes.gui.LEDIndicator import LEDIndicator
from src.classes.gui.TemperaturePlot import TemperaturePlot
from src.classes.gui.GUISetup import GUISetup
from src.classes.Config import Config
from src.classes.gui.PowerControl import PowerControl
from src.classes.devices.SSR import SSR
from src.classes.utils import (
    time_to_seconds, seconds_to_time, update_time, write_data,
    setup_gpio, stop_program, clear_inputs, set_inputs,
    set_temperature_ir, update_pzem_data, update_temperature,
    update_temp_and_humidity, update_PID, get_expected_temperature
)

################################################
# Stałe
##############################################
config = Config()
FREQ = config.get_power_value('FREQ')
HALF_CYCLE = config.get_power_value('HALF_CYCLE')
POWER = config.get_power_value('POWER')
DELAY = config.get_power_value('DELAY')
MAX_TIME_ON = config.get_power_value('MAX_TIME_ON')

##############################################
# Zmienne globalne
##############################################
root = tk.Tk()
curve_var = tk.StringVar(value=config.get_gui_value('DEFAULT_CURVE')) # Domyślna wartość z config
temp_plot = None # Globalna zmienna dla obiektu wykresu
progress_var = tk.DoubleVar(value=0) # Zmienna dla paska postępu
progress_bar = None # Globalna zmienna dla paska postępu
temperature_schedule = {}  # Dodajemy globalną zmienną dla harmonogramu temperatury

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
final_time_var = tk.StringVar(value="00:00")
temperature_ir_var = tk.DoubleVar(value="0.0")
temperature_expected_var = tk.DoubleVar(value="0.0")
temperature_approximate_var = tk.DoubleVar(value="0.0")
elapsed_time = 0
remaining_time = 0
add_time = time_to_seconds("00:00") # Dodatkowy
progres_var_percent = tk.StringVar(value="0")

temperature_curves = TemperatureCurves()
curves = temperature_curves.get_curves()

description = temperature_curves.get_curve_stage("Bisquit", "01:36:02") 


temp_calc = TemperatureApproximator()
led_indicator = LEDIndicator(root)

# Zmienne globalne dla obsługi sygnałów
global_h = None
global_ssr = None
global_root = None
global_file = None

##############################################
# GUI
############################################
def signal_handler(signum, frame):
    """Obsługa sygnałów systemowych."""
    print("Otrzymano sygnał zakończenia")
    if global_h and global_ssr and global_root:
        stop_program(global_h, global_ssr, global_root, global_file)
    sys.exit(0)

# Rejestracja obsługi sygnałów
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def setup_gui():
    """Konfiguruje interfejs użytkownika."""
    global frame, temp_plot, initial_time_var, progress_bar, led_indicator
    global global_h, global_ssr, global_root, global_file

    # Aktualizacja zmiennych globalnych
    global_h = h
    global_ssr = ssr
    global_root = root
    global_file = file

    gui_setup = GUISetup(
        root=root,
        curve_var=curve_var,
        progress_var=progress_var,
        elapsed_time_var=elapsed_time_var,
        remaining_time_var=remaining_time_var,
        final_time_var=final_time_var,
        cycle_var=cycle_var,
        impulse_after_var=impulse_after_var,
        voltage_var=voltage_var,
        current_var=current_var,
        power_var=power_var,
        energy_var=energy_var,
        temperature_thermocouple_var=temperature_thermocouple_var,
        temperature_approximate_var=temperature_approximate_var,
        temperature_expected_var=temperature_expected_var,
        temperature_ir_var=temperature_ir_var,
        bottom_cover_temperature=bottom_cover_temperature,
        humidity=humidity,
        progres_var_percent=progres_var_percent,
        curve_description=temperature_curves.get_curve_stage(curve_var.get(), "00:00:00")
    )

    def on_finish():
        """Obsługa przycisku FINISH."""
        try:
            # Wyłącz SSR
            ssr.off()
            
            # Zamknij plik CSV
            if file:
                file.close()
            
            # Zamknij GPIO
            lgpio.gpiochip_close(h)
            
            # Zamknij okno główne
            root.quit()
            root.destroy()
            
            # Wymuś zamknięcie procesu
            os._exit(0)
        except Exception as e:
            print(f"Błąd przy zamykaniu programu: {e}")
            os._exit(0)

    gui_setup.setup_gui(
        set_temperature_schedule, 
        set_initial_time, 
        set_temperature_ir, 
        on_finish
    )

    # Przypisz wartości zwracane przez GUISetup do zmiennych globalnych
    frame = gui_setup.frame
    temp_plot = gui_setup.get_temp_plot()
    initial_time_var = gui_setup.get_initial_time_var()
    progress_bar = gui_setup.get_progress_bar()
    led_indicator = gui_setup.get_led_indicator()

def set_temperature_schedule(curve_tk_var):
    """Ustawia harmonogram temperatury na podstawie wybranej krzywej."""
    global temperature_schedule, temp_plot, elapsed_time, start_time
    selected_curve_name = curve_tk_var.get()

    # Pobierz harmonogram z klasy TemperatureCurves
    temperature_schedule = temperature_curves.get_curve(selected_curve_name)
    if temperature_schedule is None:
        print(f"Nie znaleziono krzywej: {selected_curve_name}")
        return

    print(f"Wybrano krzywą: {selected_curve_name}")
    if temp_plot:
        # Resetuj czas przy zmianie harmonogramu
        elapsed_time = add_time
        start_time = time.time() - add_time
        
        # Wyczyść dane wykresu
        temp_plot.time_data = []
        temp_plot.temp_actual_data = []
        temp_plot.temp_expected_data = []
        temp_plot.line_actual.set_data([], [])
        temp_plot.line_expected.set_data([], [])
        temp_plot.line_current.set_data([], [])
        
        # Narysuj nowy profil
        temp_plot.draw_expected_profile(temperature_schedule)
        
        # Odśwież wykres
        temp_plot.canvas.draw()
        temp_plot.canvas.flush_events()
        
        # Aktualizuj wykres z początkowymi wartościami
        actual = float(temperature_approximate_var.get())
        expected = float(temperature_expected_var.get())
        temp_plot.update_plot(elapsed_time, actual, expected)

def set_initial_time():
    global add_time, elapsed_time, start_time
    try:
        # Pobierz wartość z pola tekstowego i przekonwertuj na sekundy
        time_str = initial_time_var.get()
        add_time = time_to_seconds(time_str)
        print(f"Ustawiono początkowy czas: {time_str} ({add_time} sekund)")
        
        # Aktualizuj start_time i elapsed_time
        start_time = time.time() - add_time
        elapsed_time = add_time
        
        # Aktualizuj wykres
        if temp_plot:
            # Wyczyść dane wykresu
            temp_plot.time_data = []
            temp_plot.temp_actual_data = []
            temp_plot.temp_expected_data = []
            temp_plot.line_actual.set_data([], [])
            temp_plot.line_expected.set_data([], [])
            
            # Narysuj nowy profil
            temp_plot.draw_expected_profile(temperature_schedule)
            
            # Aktualizuj wykres z początkowymi wartościami
            actual = float(temperature_approximate_var.get())
            expected = float(temperature_expected_var.get())
            temp_plot.update_plot(elapsed_time, actual, expected)
           
            # Odśwież wykres
            temp_plot.canvas.draw()
            temp_plot.canvas.flush_events()
            temp_plot.canvas_widget.update_idletasks()
            temp_plot.canvas_widget.update()
            
            # Aktualizuj etykiety czasu
            update_time()
    except Exception as e:
        print(f"Błąd przy ustawianiu początkowego czasu: {e}")

#############################
# PROGRAM GŁÓWNY
#############################

# Inicjalizacja GPIO
h = setup_gpio()

# Inicjalizacja PZEM-004T
pzem = PZEM_004T()

# Inicjalizacja I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicjalizacja termopary
thermocouple = Thermocouple()

# Inicjalizacja SSR
ssr = SSR()

# Utworzenie pliku CSV
file = open(f"dane_{curve_var.get().lower()}_{time.strftime('%Y-%m-%d_%H%M')}.csv", 
           mode="a", 
           newline=config.get_csv_value('NEWLINE'), 
           encoding=config.get_csv_value('ENCODING')) 

# Inicjalizacja GUI i wykresu
root.geometry(f"{config.get_gui_value('WINDOW_WIDTH')}x{config.get_gui_value('WINDOW_HEIGHT')}")
root.title("Kiln Control System")
setup_gui()

# Inicjalizacja harmonogramu temperatury
set_temperature_schedule(curve_var)

try:
    # Główna pętla programu
    start_time = time.time()
    current_time = start_time
    while True:

        # Odczyty sensorów i obliczenia
        try: 
            update_temperature(thermocouple, temp_calc, temperature_thermocouple_var, temperature_approximate_var)
        except Exception as e: print(f"Error updating temperature: {e}")

        # Oblicz nowe sterowanie PID
        try:
            on_delay = update_PID(temperature_approximate_var, impulse_after_var, config, temperature_curves, curve_var, elapsed_time)
        except Exception as e: print(f"Error updating PID: {e}")

        # Aktualizacja GUI i zapisu danych
        try:
            update_time(elapsed_time, temperature_schedule, elapsed_time_var, remaining_time_var, 
                       final_time_var, progress_var, progress_bar, progres_var_percent, add_time)
        except Exception as e: print(f"Error updating time labels: {e}")

        try:
            expected_temp = get_expected_temperature(temperature_curves, curve_var, elapsed_time)
            temperature_expected_var.set(f"{expected_temp:.2f}")
        except Exception as e: print(f"Error getting expected temperature: {e}")  
 

        on_delay_sek = on_delay / 1000    
        # Sterowanie triakiem
        if on_delay_sek > 0: 
            ssr.on()
            led_indicator.turn_on()
            root.update()
            time.sleep(on_delay_sek)
            ssr.off()
            led_indicator.turn_off()
            root.update()
            time.sleep(MAX_TIME_ON/1000 - on_delay_sek)
  

        # Aktualizacja danych i wykresu co 1 sekundę
        if time.time() - current_time >= 1:
            elapsed_time = time.time() - start_time  # elapsed_time będzie już uwzględniał add_time
            current_pzem_time = time.time() # Zapisz czas przed odczytami

            try: 
                update_pzem_data(pzem, voltage_var, current_var, power_var, energy_var, freq_var, cycle_var)
            except Exception as e: print(f"Error updating PZEM data: {e}")   
            
            # === Aktualizacja wykresu ===
            try:
                if temp_plot: # Sprawdź czy wykres istnieje
                    # Użyj wartości ze zmiennych Tkinter lub bezpośrednio z obliczeń
                    actual = float(temperature_approximate_var.get())
                    expected = float(temperature_expected_var.get())
                    # Używamy elapsed_time bezpośrednio
                    #print(f"Updating plot: time={elapsed_time:.2f}, actual={actual}, expected={expected}") # Debug
                    # Sprawdź, czy czas nie przekracza maksymalnego czasu harmonogramu
                    max_time = max(temperature_schedule.keys()) * 3600
                    if elapsed_time <= max_time:
                        # Aktualizuj wykres
                        temp_plot.update_plot(elapsed_time, actual, expected)
                        # Odśwież wykres
                        temp_plot.canvas.draw()
                        temp_plot.canvas.flush_events()
                        # Wyświetl aktualną pozycję pionowej linii
            except Exception as e:
                print(f"Error updating plot: {e}")
            # ==========================

            # Zaktualizuj current_time na koniec pętli aktualizacji
            current_time = current_pzem_time # Użyj zapisanego czasu dla dokładności interwału

        # Odświeżenie GUI Tkinter
        root.update_idletasks()
        root.update()

except KeyboardInterrupt:
    ssr.off()
    print("Zatrzymano program przerwaniem.")
finally:
    file.close()
    del ssr  # Wywoła destruktor, który zamknie GPIO