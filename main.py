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
from src.classes.calculates.TemperatureApproximator import TemperatureApproximator
from src.classes.controllers.PIDController import PIDController
from src.classes.calculates.TemperatureCurves import TemperatureCurves
from src.classes.gui.LEDIndicator import LEDIndicator
from src.classes.gui.TemperaturePlot import TemperaturePlot
from src.classes.gui.GUISetup import GUISetup
from src.classes.config.Config import Config
from src.classes.gui.PowerControl import PowerControl
from src.classes.devices.SSR import SSR
from src.classes.logger.CSVLogger import CSVLogger
from src.classes.state.GlobalState import GlobalState
from src.classes.controllers.GUIController import GUIController
from src.classes.utils.utils import (
    time_to_seconds, seconds_to_time, update_time, write_data,
    setup_gpio, stop_program, clear_inputs, set_inputs,
    set_temperature_ir, update_pzem_data, update_temperature,
    update_temp_and_humidity, update_PID, get_expected_temperature
)

##############################################
# GUI
############################################
def signal_handler(signum, frame):
    """Obsługa sygnałów systemowych."""
    print("Otrzymano sygnał zakończenia")
    if state.global_h and state.global_ssr and state.global_root:
        stop_program(state.global_h, state.global_ssr, state.global_root, state.global_file)
    sys.exit(0)

# Rejestracja obsługi sygnałów
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def setup_gui():
    """Konfiguruje interfejs użytkownika."""
    # Aktualizacja zmiennych globalnych
    state.global_h = state.h
    state.global_ssr = state.ssr
    state.global_root = state.root
    state.global_file = state.csv_logger

    # Pobierz domyślną krzywą z konfiguracji
    default_curve = state.config.get_gui_value('DEFAULT_CURVE')
    curve_description = state.temperature_curves.get_curve_stage(default_curve, "00:00:00")

    gui_setup = GUISetup(
        root=state.root,
        curve_var=state.curve_var,
        progress_var=state.progress_var,
        elapsed_time_var=state.elapsed_time_var,
        remaining_time_var=state.remaining_time_var,
        final_time_var=state.final_time_var,
        cycle_var=state.cycle_var,
        impulse_after_var=state.impulse_after_var,
        voltage_var=state.voltage_var,
        current_var=state.current_var,
        power_var=state.power_var,
        energy_var=state.energy_var,
        temperature_thermocouple_var=state.temperature_thermocouple_var,
        temperature_approximate_var=state.temperature_approximate_var,
        temperature_expected_var=state.temperature_expected_var,
        temperature_ir_var=state.temperature_ir_var,
        bottom_cover_temperature=state.bottom_cover_temperature,
        humidity=state.humidity,
        progres_var_percent=state.progres_var_percent,
        curve_description=curve_description,
        hours_var=state.hours_var,
        minutes_var=state.minutes_var
    )

    def on_finish():
        """Obsługa przycisku FINISH."""
        try:
            # Wyłącz SSR
            state.ssr.off()
            
            # Zamknij logger CSV
            if state.csv_logger:
                state.csv_logger.close()
            
            # Zamknij GPIO
            lgpio.gpiochip_close(state.h)
            
            # Zamknij okno główne
            state.root.quit()
            state.root.destroy()
            
            # Wymuś zamknięcie procesu
            os._exit(0)
        except Exception as e:
            print(f"Błąd przy zamykaniu programu: {e}")
            os._exit(0)

    gui_setup.setup_gui(
        gui_controller.set_temperature_schedule, 
        gui_controller.set_initial_time, 
        lambda: gui_controller.set_temperature_ir_wrapper(gui_setup), 
        on_finish
    )

    # Przypisz wartości zwracane przez GUISetup do zmiennych stanu
    state.frame = gui_setup.frame
    state.temp_plot = gui_setup.get_temp_plot()
    state.initial_time_var = gui_setup.get_initial_time_var()
    state.progress_bar = gui_setup.get_progress_bar()
    state.led_indicator = gui_setup.get_led_indicator()

#############################
# PROGRAM GŁÓWNY
#############################

# Inicjalizacja stanu globalnego
state = GlobalState(init_gui=False)

# Inicjalizacja kontrolera GUI
gui_controller = GUIController(state)

# Inicjalizacja GPIO
state.h = state.setup_gpio()

# Inicjalizacja PZEM-004T
state.pzem = PZEM_004T()

# Inicjalizacja I2C
state.i2c = busio.I2C(board.SCL, board.SDA)

# Inicjalizacja termopary
state.thermocouple = Thermocouple()

# Inicjalizacja SSR
state.ssr = SSR()

# Inicjalizacja GUI i wykresu
state.init_gui()  # Inicjalizuje główne okno i zmienne Tkinter

# Poczekaj na utworzenie głównego okna
if not state.root:
    raise RuntimeError("Nie udało się utworzyć głównego okna")

# Inicjalizacja interfejsu użytkownika
setup_gui()  # Używa zmiennych Tkinter

# Inicjalizacja loggera CSV
state.setup_csv_logger()

# Inicjalizacja harmonogramu temperatury
gui_controller.set_temperature_schedule(state.curve_var)

# Inicjalizacja zmiennych
last_pzem_update = 0
pzem_update_interval = 1.0  # Aktualizacja co sekundę

try:
    # Główna pętla programu
    state.reset_time()
    last_gui_update = time.time()
    last_plot_update = time.time()
    last_csv_update = time.time()
    
    while True:
        current_time = time.time()
        
        # Aktualizacja GUI co 100ms
        if current_time - last_gui_update >= 0.1:
            last_gui_update = current_time
            
            # Odczyty sensorów i obliczenia
            try: 
                update_temperature(state.thermocouple, state.temp_calc, 
                                state.temperature_thermocouple_var, 
                                state.temperature_approximate_var)
            except Exception as e: 
                print(f"Error updating temperature: {e}")

            # Oblicz nowe sterowanie PID
            try:
                state.on_delay = update_PID(
                    state.temperature_approximate_var, 
                    state.impulse_after_var, 
                    state.config, 
                    state.temperature_curves, 
                    state.curve_var,
                    state.elapsed_time
                )
            except Exception as e: 
                print(f"Error updating PID: {e}")

            # Aktualizacja stanu SSR i kontrolki LED
            on_delay_sek = state.on_delay / 1000    
            # Sterowanie triakiem
            if on_delay_sek > 0: 
                state.ssr.on()
                state.led_indicator.turn_on()
                state.root.update()
                time.sleep(on_delay_sek)
                state.ssr.off()
                state.led_indicator.turn_off()
                state.root.update()

            state.update_time()

            # Aktualizacja etykiet czasu
            try:
                update_time(
                    state.elapsed_time, 
                    state.temperature_schedule, 
                    state.elapsed_time_var, 
                    state.remaining_time_var, 
                    state.final_time_var, 
                    state.progress_var, 
                    state.progress_bar, 
                    state.progres_var_percent, 
                    state.add_time,
                    state.curve_description_var.get() if state.curve_description_var else "",
                    state.curve_description_var
                )
            except Exception as e: 
                print(f"Error updating time labels: {e}")

            # Aktualizacja oczekiwanej temperatury
            try:
                expected_temp = get_expected_temperature(
                    state.temperature_curves, 
                    state.curve_var, 
                    state.elapsed_time
                )
                state.temperature_expected_var.set(f"{expected_temp:.2f}")
            except Exception as e: 
                print(f"Error getting expected temperature: {e}")

            # Aktualizacja danych PZEM co sekundę
            if current_time - last_pzem_update >= pzem_update_interval:
                try: 
                    update_pzem_data(
                        state.pzem, 
                        state.voltage_var, 
                        state.current_var, 
                        state.power_var, 
                        state.energy_var, 
                        state.freq_var, 
                        state.cycle_var
                    )
                    last_pzem_update = current_time
                except Exception as e: 
                    print(f"Error updating PZEM data: {e}")

            # Odświeżenie GUI
            state.root.update_idletasks()
            state.root.update()

        # Aktualizacja wykresu co 10 sekund
        if current_time - last_plot_update >= 10:
            last_plot_update = current_time
            try:
                if state.temp_plot and state.temperature_schedule and 'points' in state.temperature_schedule:
                    actual = float(state.temperature_approximate_var.get())
                    state.temp_plot.update_plot(state.elapsed_time, actual)
            except Exception as e:
                print(f"Error updating plot: {e}")

        # Zapis do CSV co 1 sekundę
        if current_time - last_csv_update >= 10:
            last_csv_update = current_time
            try:
                state.csv_logger.write_data([
                    time.strftime("%Y-%m-%d %H:%M:%S"),
                    state.elapsed_time,
                    state.temperature_thermocouple_var.get(),
                    state.temperature_approximate_var.get(),
                    state.temperature_expected_var.get(),
                    state.voltage_var.get(),
                    state.current_var.get(),
                    state.power_var.get(),
                    state.energy_var.get(),
                    state.freq_var.get(),
                    state.cycle_var.get()
                ])
            except Exception as e:
                print(f"Error writing to CSV: {e}")

        state.update_time()
        time.sleep(0.01)  # Dodaj małe opóźnienie, aby zmniejszyć obciążenie CPU

except KeyboardInterrupt:
    state.ssr.off()
    print("Zatrzymano program przerwaniem.")
finally:
    state.cleanup()