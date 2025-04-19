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

from PZEM_004T import PZEM_004T
from Thermocouple import Thermocouple
from TemperatureApproximator import TemperatureApproximator
from PIDController import PIDController
from src.classes.TemperatureCurves import TemperatureCurves
from src.classes.LEDIndicator import LEDIndicator

################################################
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
curve_var = tk.StringVar(value="Glazing") # Domyślna wartość
temp_plot = None # Globalna zmienna dla obiektu wykresu
progress_var = tk.DoubleVar(value=0) # Zmienna dla paska postępu
progress_bar = None # Globalna zmienna dla paska postępu

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

# Definicje krzywych temperatury
Bisquit = {
    0: 30,
    3: 200,
    4: 400,
    5: 500,
    6: 600,
    7: 850,
    7.25: 850,
    8: 600,
    9: 500,
    10: 200,
    11: 30
}

Bisquit_express = {
    0: 30,
    3: 500,
    4: 600,
    5: 850,
    5.25: 850,
    6: 600,
    7: 500,
    8: 30
}

Glazing = {
    0: 30,
    1: 200,
    2: 500,
    3: 600,
    4.00: 1050,
    4.25: 1050,
    5: 850,
    6: 600,
    7: 500,
    8: 200,
    9: 30
}

Glazing_perfect = {
    0: 30,
    1: 200,
    2: 500,
    3: 600,
    4: 750,
    5: 900,
    6.00: 1050,
    6.25: 1050,
    7: 850,
    8: 600,
    9: 500,
    10: 30,
}

Glazing_express = {
    0: 30,
    2.00: 1000,
    2.25: 1030,
    3.00: 30
}

temp_calc = TemperatureApproximator()
led_indicator = LEDIndicator(root)

##############################################
# Klasa do obsługi wykresu
##############################################
class TemperaturePlot:
    def __init__(self, parent_frame):
        self.fig = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.ax.set_title("Temperature Profile")
        self.ax.set_xlabel("Time (HH:MM)")
        self.ax.set_ylabel("Temperature (°C)")

        # Lines for expected and actual temperature
        self.line_expected, = self.ax.plot([], [], 'r--', label='Expected')
        self.line_actual, = self.ax.plot([], [], 'b-', label='Actual')
        # Line for the entire profile
        self.line_profile, = self.ax.plot([], [], 'g:', label='Profile')
        # Vertical line for current point
        self.line_current = self.ax.axvline(x=0, color='r', linestyle='-', linewidth=2, label='Current point', picker=5)

        # Ustawienie formatera osi X
        def time_formatter(x, pos):
            hours = int(x // 3600)
            minutes = int((x % 3600) // 60)
            return f"{hours:02}:{minutes:02}"
        
        self.ax.xaxis.set_major_formatter(plt.FuncFormatter(time_formatter))

        self.ax.legend()
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Dane do wykresu
        self.time_data = []
        self.temp_actual_data = []
        self.temp_expected_data = []
        self.profile_times = []
        self.profile_temps = []

        # Zmienne do przeciągania linii
        self.dragging = False
        self.drag_start_x = 0
        self.drag_current_x = 0

        # Podłącz obsługę zdarzeń myszy
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('axes_enter_event', self.on_axes_enter)
        self.canvas.mpl_connect('axes_leave_event', self.on_axes_leave)

    def on_pick(self, event):
        if event.artist == self.line_current:
            self.canvas_widget.config(cursor="sb_h_double_arrow")

    def on_axes_enter(self, event):
        if event.inaxes == self.ax:
            self.canvas_widget.config(cursor="arrow")

    def on_axes_leave(self, event):
        self.canvas_widget.config(cursor="arrow")

    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        if self.line_current.contains(event)[0]:
            self.dragging = True
            self.drag_start_x = event.xdata
            self.drag_current_x = event.xdata
            self.canvas_widget.config(cursor="sb_h_double_arrow")

    def on_release(self, event):
        if self.dragging:
            self.dragging = False
            self.canvas_widget.config(cursor="arrow")
            if event.inaxes != self.ax:
                return
            if hasattr(event, 'xdata') and event.xdata is not None:
                self.update_time_from_line(event.xdata)

    def on_motion(self, event):
        if not self.dragging or event.inaxes != self.ax:
            return
        if hasattr(event, 'xdata') and event.xdata is not None:
            # Ogranicz ruch linii do zakresu wykresu
            xdata = max(0, min(event.xdata, max(self.profile_times)))
            self.drag_current_x = xdata
            # Aktualizuj tylko pozycję linii
            self.line_current.set_xdata([xdata, xdata])
            # Odśwież tylko linię
            self.ax.draw_artist(self.line_current)
            self.canvas.blit(self.ax.bbox)

    def update_time_from_line(self, xdata):
        global elapsed_time, start_time, add_time
        # Ogranicz wartość do zakresu wykresu
        xdata = max(0, min(xdata, max(self.profile_times)))
        
        # Aktualizuj czasy
        add_time = xdata
        elapsed_time = xdata
        start_time = time.time() - xdata
        
        # Aktualizuj pole tekstowe
        hours = int(xdata // 3600)
        minutes = int((xdata % 3600) // 60)
        initial_time_var.set(f"{hours:02}:{minutes:02}")
        
        # Resetuj dane wykresu
        self.time_data = []
        self.temp_actual_data = []
        self.temp_expected_data = []
        self.line_actual.set_data([], [])
        self.line_expected.set_data([], [])
        
        # Aktualizuj wykres
        actual = float(temperature_approximate_var.get())
        expected = float(temperature_expected_var.get())
        self.update_plot(xdata, actual, expected)
        
        # Aktualizuj etykiety czasu
        update_time()
        
        print(f"Ustawiono czas z linii: {xdata} sekund ({hours:02}:{minutes:02})")

    def update_plot(self, time_point, actual_temp, expected_temp):
        """Dodaje nowy punkt danych i aktualizuje wykres."""
        self.time_data.append(time_point)
        self.temp_actual_data.append(actual_temp)
        self.temp_expected_data.append(expected_temp)

        # Aktualizacja danych linii
        self.line_actual.set_data(self.time_data, self.temp_actual_data)
        self.line_expected.set_data(self.time_data, self.temp_expected_data)
        
        # Aktualizacja pionowej linii aktualnego punktu
        if self.profile_times:
            # Usuń starą linię pionową
            self.line_current.remove()
            # Utwórz nową linię pionową
            self.line_current = self.ax.axvline(x=time_point, color='r', linestyle='-', linewidth=2, picker=5)
            #print(f"Updating current line: x={time_point}") # Debug

        # Ustawienie limitów osi Y na podstawie profilu + margines
        if self.profile_temps:
            min_temp = min(self.profile_temps)
            max_temp = max(self.profile_temps)
            margin = (max_temp - min_temp) * 0.1
            self.ax.set_ylim(bottom=min_temp - margin, top=max_temp + margin)

        # Ustawienie limitów osi X na podstawie profilu zadanego
        if self.profile_times:
            self.ax.set_xlim(left=0, right=max(self.profile_times) * 1.05)

        # Odświeżenie wykresu
        self.canvas.draw()
        self.canvas.flush_events()
        self.fig.canvas.draw_idle()
        self.canvas_widget.update_idletasks()
        self.canvas_widget.update()

    def draw_expected_profile(self, schedule):
        """Rysuje cały oczekiwany profil temperatury na podstawie harmonogramu."""
        # Konwersja godzin na sekundy
        schedule_seconds = {k * 3600: v for k, v in schedule.items()}
        self.profile_times = sorted(schedule_seconds.keys())
        self.profile_temps = [schedule_seconds[t] for t in self.profile_times]

        # Ustawienie danych dla linii profilu
        self.line_profile.set_data(self.profile_times, self.profile_temps)

        # Ustawienie limitów osi Y na podstawie profilu + margines
        min_temp = min(self.profile_temps)
        max_temp = max(self.profile_temps)
        margin = (max_temp - min_temp) * 0.1
        self.ax.set_ylim(bottom=min_temp - margin, top=max_temp + margin)

        # Ustawienie limitu osi X na podstawie maksymalnego czasu profilu
        if self.profile_times:
            self.ax.set_xlim(left=0, right=max(self.profile_times) * 1.05)

        # Wyczyść dane bieżące przy zmianie profilu
        self.time_data = []
        self.temp_actual_data = []
        self.temp_expected_data = []
        self.line_actual.set_data([], [])
        self.line_expected.set_data([], [])
        if hasattr(self, 'line_current'):
            self.line_current.remove()
            self.line_current = self.ax.axvline(x=0, color='r', linestyle='-', linewidth=2, picker=5)

        self.ax.legend()
        self.canvas.draw()
        self.canvas.flush_events()
        self.canvas_widget.update_idletasks()
        self.canvas_widget.update()

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
    try:
        triac_pin_set_zero()
        lgpio.gpiochip_close(h)
    except Exception as e:
        print(f"Błąd przy zamykaniu GPIO: {e}")
    print("Zatrzymano program przyciskiem")
    root.quit()  # Zamiast exit(0) używamy root.quit()

def triac_pin_set_zero():
    lgpio.gpio_claim_output(h, TRIAC_PIN)
    lgpio.gpio_write(h, TRIAC_PIN, 0)  

def regulation_desk():        
    root.geometry("640x820")
    root.title("Kiln Control System")

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
    global elapsed_time, remaining_time, progres_var_percent
    hours, remainder = divmod(int(elapsed_time), 3600)
    minutes, seconds = divmod(remainder, 60)
    elapsed_time_var.set(f"{hours:02}:{minutes:02}:{seconds:02}")
    
    print(f"Elapsed time: {hours:02}:{minutes:02}:{seconds:02}")

    # Oblicz pozostały czas na podstawie harmonogramu
    total_schedule_time = max(temperature_schedule.keys()) * 3600
    remaining_time = max(0, total_schedule_time - elapsed_time)
    
    hours, remainder = divmod(int(remaining_time), 3600)
    minutes, seconds = divmod(remainder, 60)
    remaining_time_var.set(f"{hours:02}:{minutes:02}:{seconds:02}") 

    # Oblicz postęp
    if total_schedule_time > 0:
        progress = (elapsed_time / total_schedule_time) * 100
        progress_var.set(progress)  # Aktualizuj wartość paska postępu
        if progress_bar:  # Sprawdź czy progress_bar istnieje
            progress_bar.update()  # Wymuś odświeżenie paska postępu
    else:
        progress_var.set(0)
        if progress_bar:
            progress_bar.update()

    # Oblicz przewidywany czas zakończenia
    final_time = time.strftime("%H:%M:%S", time.localtime(time.time() + remaining_time + add_time))
    final_time_var.set(final_time)

    progres_var_percent.set(f"{progress:.2f}%")

    
def update_PID():
    global elapsed_time, on_delay, impulse_after_var
    setpoint = get_expected_temperature()
    pid = PIDController(setpoint, Kp=160, Ki=80, Kd=4)
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
def setup_gui():
    global frame, temp_plot, initial_time_var, progress_bar, led_indicator

    # Frame for controls (upper part)
    controls_frame = tk.Frame(root)
    controls_frame.pack(pady=(10, 0), fill=tk.X)

    # === GUI elements moved to controls_frame ===
    curve_option_menu = tk.OptionMenu(controls_frame, curve_var, "Bisquit", "Bisquit_express", "Glazing", "Glazing_perfect", "Glazing_express", command=lambda sel=curve_var: set_temperature_schedule(curve_var))
    curve_option_menu.config(width=15)
    curve_option_menu.pack(pady=(10, 10))

    # Frame for initial time
    initial_time_frame = tk.Frame(controls_frame)
    initial_time_frame.pack(pady=5)
    tk.Label(initial_time_frame, text="Initial time (HH:MM):").pack(side=tk.LEFT, padx=5)
    initial_time_var = tk.StringVar(value="01:00")
    initial_time_entry = tk.Entry(initial_time_frame, textvariable=initial_time_var, width=5)
    initial_time_entry.pack(side=tk.LEFT, padx=5)
    tk.Button(initial_time_frame, text="SET", command=set_initial_time).pack(side=tk.LEFT, padx=5)

    # Progress bar
    progress_bar = ttk.Progressbar(controls_frame, variable=progress_var, maximum=100, length=500, style="blue.Horizontal.TProgressbar")
    progress_bar.pack(pady=(0, 5))
    
    style = ttk.Style()
    style.configure("blue.Horizontal.TProgressbar", troughcolor='white', background='navy', thickness=25)
    progress_label = tk.Label(controls_frame, textvariable=progres_var_percent, anchor="center", fg="white", bg="navy")
    progress_label.place(in_=progress_bar, relx=0.5, rely=0.5, anchor="center")

    # Frame for labels and values
    info_frame = tk.Frame(controls_frame)
    info_frame.pack(pady=5)

    # Labels and values in grid
    tk.Label(info_frame, text="Elapsed Time:").grid(row=0, column=0, padx=5, sticky="w")
    tk.Label(info_frame, textvariable=elapsed_time_var).grid(row=0, column=1, padx=5, sticky="w")
    tk.Label(info_frame, text="Remaining Time:").grid(row=1, column=0, padx=5, sticky="w")
    tk.Label(info_frame, textvariable=remaining_time_var).grid(row=1, column=1, padx=5, sticky="w")
    tk.Label(info_frame, text="Final time:").grid(row=2, column=0, padx=5, sticky="w")
    tk.Label(info_frame, textvariable=final_time_var).grid(row=2, column=1, padx=5, sticky="w")

    tk.Label(info_frame, text="Cycle (ms):").grid(row=0, column=2, padx=5, sticky="w")
    tk.Label(info_frame, textvariable=cycle_var).grid(row=0, column=3, padx=5, sticky="w")
    tk.Label(info_frame, text="Triac on (ms):", fg="maroon").grid(row=1, column=2, padx=5, sticky="w")
    tk.Label(info_frame, textvariable=impulse_after_var, fg="maroon").grid(row=1, column=3, padx=5, sticky="w")

    tk.Label(info_frame, text="Voltage (V):").grid(row=3, column=0, padx=5, sticky="w")
    tk.Label(info_frame, textvariable=voltage_var).grid(row=3, column=1, padx=5, sticky="w")
    tk.Label(info_frame, text="Current (A):").grid(row=4, column=0, padx=5, sticky="w")
    tk.Label(info_frame, textvariable=current_var).grid(row=4, column=1, padx=5, sticky="w")
    tk.Label(info_frame, text="Power (W):", fg="maroon").grid(row=5, column=0, padx=5, sticky="w")
    tk.Label(info_frame, textvariable=power_var, fg="maroon").grid(row=5, column=1, padx=5, sticky="w")
    tk.Label(info_frame, text="Energy (Wh):").grid(row=6, column=0, padx=5, sticky="w")
    tk.Label(info_frame, textvariable=energy_var).grid(row=6, column=1, padx=5, sticky="w")

    tk.Label(info_frame, text="Thermocouple (°C):").grid(row=3, column=2, padx=5, sticky="w")
    tk.Label(info_frame, textvariable=temperature_thermocouple_var).grid(row=3, column=3, padx=5, sticky="w")
    tk.Label(info_frame, text="Temp. Approx (°C):", fg="maroon").grid(row=4, column=2, padx=5, sticky="w")
    tk.Label(info_frame, textvariable=temperature_approximate_var, fg="maroon").grid(row=4, column=3, padx=5, sticky="w")
    tk.Label(info_frame, text="Temp. Expected (°C):", fg="maroon").grid(row=5, column=2, padx=5, sticky="w")
    tk.Label(info_frame, textvariable=temperature_expected_var, fg="maroon").grid(row=5, column=3, padx=5, sticky="w")

    # Frame for IR correction
    ir_frame = tk.Frame(controls_frame)
    ir_frame.pack(pady=5)
    tk.Label(ir_frame, text="Corrective temperature IR (°C):").pack(side=tk.LEFT, padx=5)
    spinbox_temperature_ir_var = tk.Spinbox(ir_frame, from_=-1000, to=1000, increment=1, textvariable=temperature_ir_var, width=5)
    spinbox_temperature_ir_var.pack(side=tk.LEFT, padx=5)
    tk.Button(ir_frame, text="SET", command=set_temperature_ir).pack(side=tk.LEFT, padx=5)

    # FINISH button at the bottom of controls frame
    tk.Button(controls_frame, text="FINISH", command=stop_program).pack(pady=(10, 10))

    # === Plot frame (lower part) ===
    plot_frame = tk.Frame(root)
    plot_frame.pack(pady=(0, 10), padx=10, fill=tk.BOTH, expand=True)
    temp_plot = TemperaturePlot(plot_frame)

    # Set initial schedule on the plot
    set_temperature_schedule(curve_var)

    # Initialize LED indicator
    led_indicator = LEDIndicator(plot_frame)
    led_indicator.place(relx=0.95, rely=0.05, anchor="ne")
    led_indicator.configure(bg="white")
    led_indicator.configure(width=20)
    led_indicator.configure(height=20)

# Usunięcie starego tworzenia ramki
# frame = tk.Frame(root)
# frame.pack(pady=(10, 10))


def set_temperature_schedule(curve_tk_var):
    """Ustawia harmonogram temperatury na podstawie wybranej krzywej."""
    global temperature_schedule, temp_plot, elapsed_time, start_time
    selected_curve_name = curve_tk_var.get()

    # Mapowanie nazw z OptionMenu na słowniki z danymi
    schedule_map = {
        "Glazing": Glazing,
        "Bisquit": Bisquit,
        "Bisquit_express": Bisquit_express,     
        "Glazing_perfect": Glazing_perfect,
        "Glazing_express": Glazing_express
    }

    if selected_curve_name in schedule_map:
        temperature_schedule = schedule_map[selected_curve_name]
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
            
            # Wyświetl informacje debugowe
            #print(f"Profile times: {temp_plot.profile_times}")
            #print(f"Profile temps: {temp_plot.profile_temps}")
            #print(f"Start time: {start_time}")
            #print(f"Add time: {add_time}")
            #print(f"Elapsed time: {elapsed_time}")
    else:
        print(f"Nieznana krzywa: {selected_curve_name}")

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
            
            # Wyświetl informacje debugowe
            #print(f"Profile times: {temp_plot.profile_times}")
            #print(f"Profile temps: {temp_plot.profile_temps}")
            #print(f"Start time: {start_time}")
            #print(f"Add time: {add_time}")
            #print(f"Elapsed time: {elapsed_time}")
            
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
setup_gpio()

# Inicjalizacja PZEM-004T
pzem = PZEM_004T()

# Inicjalizacja I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicjalizacja termopary
thermocouple = Thermocouple()

# Inicjalizacja GUI i wykresu
root.geometry("900x1000") # Zwiększ rozmiar okna, aby pomieścić wykres
root.title("Kiln Control System")
setup_gui() # Wywołaj nową funkcję konfiguracji GUI

# Utworzenie pliku CSV - przeniesione po setup_gui()
file = open(f"dane_{curve_var.get().lower()}_{time.strftime('%Y-%m-%d_%H%M')}.csv", mode="a", newline="", encoding="utf-8")

try:
    # Główna pętla programu
    start_time = time.time()
    current_time = start_time
    while True:

        if on_delay > 0:
            lgpio.gpio_write(h, TRIAC_PIN, 1)
            led_indicator.turn_on()
            root.update()
            time.sleep(on_delay/1000)
            lgpio.gpio_write(h, TRIAC_PIN, 0)
            led_indicator.turn_off()
            root.update()
            time.sleep(1 - on_delay/1000) # Czy off_delay jest potrzebne? Zwykle steruje się tylko czasem włączenia
        else:
            time.sleep(1)
  

        # Aktualizacja danych i wykresu co 0.5 sekundy
        if time.time() - current_time >= 0.5:
            elapsed_time = time.time() - start_time  # elapsed_time będzie już uwzględniał add_time
            current_pzem_time = time.time() # Zapisz czas przed odczytami

            # Odczyty sensorów i obliczenia
            try: update_temperature(thermocouple)
            except Exception as e: print(f"Error updating temperature: {e}")
            try: update_pzem_data(pzem)
            except Exception as e: print(f"Error updating PZEM data: {e}")
            try:
                 expected_temp = get_expected_temperature()
                 temperature_expected_var.set(f"{expected_temp:.2f}")
            except Exception as e: print(f"Error getting expected temperature: {e}")
            try: update_PID() # Oblicz nowe sterowanie PID
            except Exception as e: print(f"Error updating PID: {e}")

            # Aktualizacja GUI i zapisu danych
            try: update_time() # Aktualizuje etykiety czasu i postępu
            except Exception as e: print(f"Error updating time labels: {e}")

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
    triac_pin_set_zero()
    print("Zatrzymano program przerwaniem.")
finally:
    file.close()
    lgpio.gpiochip_close(h)