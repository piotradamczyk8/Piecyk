import tkinter as tk
from tkinter import ttk
from typing import Optional
from src.classes.gui.TemperaturePlot import TemperaturePlot
from src.classes.gui.LEDIndicator import LEDIndicator
from src.classes.calculates.TemperatureCurves import TemperatureCurves

class GUISetup:
    def __init__(self, root: tk.Tk, curve_var: tk.StringVar, progress_var: tk.DoubleVar,
                 elapsed_time_var: tk.StringVar, remaining_time_var: tk.StringVar,
                 final_time_var: tk.StringVar, cycle_var: tk.StringVar,
                 impulse_after_var: tk.StringVar, voltage_var: tk.StringVar,
                 current_var: tk.StringVar, power_var: tk.StringVar,
                 energy_var: tk.StringVar, temperature_thermocouple_var: tk.StringVar,
                 temperature_approximate_var: tk.StringVar, temperature_expected_var: tk.StringVar,
                 temperature_ir_var: tk.StringVar, bottom_cover_temperature: tk.StringVar,
                 humidity: tk.StringVar, progres_var_percent: tk.StringVar,
                 curve_description: str = "", hours_var: tk.StringVar = None,
                 minutes_var: tk.StringVar = None):
        self.root = root
        self.curve_var = curve_var
        self.progress_var = progress_var
        self.elapsed_time_var = elapsed_time_var
        self.remaining_time_var = remaining_time_var
        self.final_time_var = final_time_var
        self.cycle_var = cycle_var
        self.impulse_after_var = impulse_after_var
        self.voltage_var = voltage_var
        self.current_var = current_var
        self.power_var = power_var
        self.energy_var = energy_var
        self.temperature_thermocouple_var = temperature_thermocouple_var
        self.temperature_approximate_var = temperature_approximate_var
        self.temperature_expected_var = temperature_expected_var
        self.temperature_ir_var = temperature_ir_var
        self.bottom_cover_temperature = bottom_cover_temperature
        self.humidity = humidity
        self.progres_var_percent = progres_var_percent
        self.curve_description_var = tk.StringVar(master=self.root, value=curve_description)
        self.initial_time_var = tk.StringVar(master=self.root, value="00:00")
        self.hours_var = hours_var
        self.minutes_var = minutes_var

        self.frame: Optional[tk.Frame] = None
        self.temp_plot = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.led_indicator = None
        self.spinbox_temperature_ir = None

        # Inicjalizacja TemperatureCurves
        self.temperature_curves = TemperatureCurves()
        

    def setup_gui(self, set_temperature_schedule, set_initial_time, set_temperature_ir, stop_program):
        """Konfiguruje interfejs użytkownika."""
        # Frame for controls (upper part)
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=(10, 0), fill=tk.X)

        # === GUI elements moved to controls_frame ===
        # Pobierz dostępne krzywe z TemperatureCurves i usuń puste wartości
        available_curves = [curve for curve in self.temperature_curves.get_curves() if curve.strip()]
        
        # Sortuj krzywe alfabetycznie
        available_curves = sorted(available_curves)
        
        # Utwórz menu wyboru krzywej
        if available_curves:
            self.curve_var.set(available_curves[0])  # Ustaw pierwszą krzywą jako domyślną
            
            # Frame dla comboboxa
            curve_frame = tk.Frame(controls_frame)
            curve_frame.pack(pady=(10, 10), fill=tk.X, anchor=tk.CENTER)
            
            # Combobox 
            curve_combobox = ttk.Combobox(
                curve_frame,
                textvariable=self.curve_var,
                values=available_curves,
                state="readonly",           
                width=60  # szerokość w znakach
            )
            curve_combobox.pack(side=tk.LEFT, padx=200, fill=tk.X, expand=False, anchor=tk.CENTER)
            
            # Dodaj obsługę zmiany krzywej
            def on_curve_change(event):
                set_temperature_schedule(self.curve_var)
                # Aktualizuj tytuł wykresu
                if self.temp_plot:
                    self.temp_plot.set_title(f"Temperature Profile {self.curve_var.get()}")
                
            curve_combobox.bind('<<ComboboxSelected>>', on_curve_change)
            
        else:
            # Jeśli nie ma dostępnych krzywych, wyświetl komunikat
            tk.Label(controls_frame, text="Brak dostępnych krzywych").pack(pady=(10, 10))


        # Frame for initial time
        initial_time_frame = tk.Frame(controls_frame)
        initial_time_frame.pack(pady=5)
        
        tk.Label(initial_time_frame, text="Initial Time:").pack(side=tk.LEFT)
        
        # Spinbox dla godzin
        self.hours_spinbox = tk.Spinbox(
            initial_time_frame,
            from_=0,
            to=23,
            width=2,
            format="%02.0f",
            textvariable=self.hours_var
        )
        self.hours_spinbox.pack(side=tk.LEFT, padx=2)
        
        tk.Label(initial_time_frame, text=":").pack(side=tk.LEFT)
        
        # Spinbox dla minut
        self.minutes_spinbox = tk.Spinbox(
            initial_time_frame,
            from_=0,
            to=59,
            width=2,
            format="%02.0f",
            textvariable=self.minutes_var
        )
        self.minutes_spinbox.pack(side=tk.LEFT, padx=2)

        tk.Button(initial_time_frame, text="SET", command=set_initial_time).pack(side=tk.LEFT, padx=5)

        # Frame for curve description
        description_frame = tk.Frame(controls_frame)
        description_frame.pack(pady=5, fill=tk.X)
        tk.Label(description_frame, text="").pack(side=tk.TOP, padx=10)
        description_label = tk.Label(description_frame, textvariable=self.curve_description_var, wraplength=400)
        description_label.pack(side=tk.TOP, padx=10, fill=tk.X, expand=True)

        # Progress bar
        self.progress_bar = ttk.Progressbar(controls_frame, variable=self.progress_var, 
                                          maximum=100, length=500, style="blue.Horizontal.TProgressbar")
        self.progress_bar.pack(pady=(0, 5))
        
        style = ttk.Style()
        style.configure("blue.Horizontal.TProgressbar", troughcolor='white', background='navy', thickness=25)
        progress_label = tk.Label(controls_frame, textvariable=self.progres_var_percent, 
                                anchor="center", fg="white", bg="navy")
        progress_label.place(in_=self.progress_bar, relx=0.5, rely=0.5, anchor="center")

        # Frame for labels and values
        info_frame = tk.Frame(controls_frame)
        info_frame.pack(pady=5)

        # Labels and values in grid
        tk.Label(info_frame, text="Elapsed Time:").grid(row=0, column=0, padx=10, sticky="w")
        tk.Label(info_frame, textvariable=self.elapsed_time_var).grid(row=0, column=1, padx=10, sticky="w")
        tk.Label(info_frame, text="Remaining Time:").grid(row=1, column=0, padx=10, sticky="w")
        tk.Label(info_frame, textvariable=self.remaining_time_var).grid(row=1, column=1, padx=10, sticky="w")
        tk.Label(info_frame, text="Final time:").grid(row=2, column=0, padx=10, sticky="w")
        tk.Label(info_frame, textvariable=self.final_time_var).grid(row=2, column=1, padx=10, sticky="w")

        tk.Label(info_frame, text="Cycle (ms):").grid(row=0, column=2, padx=10, sticky="w")
        tk.Label(info_frame, textvariable=self.cycle_var).grid(row=0, column=3, padx=10, sticky="w")
        tk.Label(info_frame, text="Triac on (ms):", fg="maroon").grid(row=1, column=2, padx=10, sticky="w")
        tk.Label(info_frame, textvariable=self.impulse_after_var, fg="maroon").grid(row=1, column=3, padx=10, sticky="w")

        tk.Label(info_frame, text="Voltage (V):").grid(row=3, column=0, padx=10, sticky="w")
        tk.Label(info_frame, textvariable=self.voltage_var).grid(row=3, column=1, padx=10, sticky="w")
        tk.Label(info_frame, text="Current (A):").grid(row=4, column=0, padx=10, sticky="w")
        tk.Label(info_frame, textvariable=self.current_var).grid(row=4, column=1, padx=10, sticky="w")
        tk.Label(info_frame, text="Power (W):", fg="maroon").grid(row=5, column=0, padx=10, sticky="w")
        tk.Label(info_frame, textvariable=self.power_var, fg="maroon").grid(row=5, column=1, padx=10, sticky="w")
        tk.Label(info_frame, text="Energy (Wh):").grid(row=6, column=0, padx=10, sticky="w")
        tk.Label(info_frame, textvariable=self.energy_var).grid(row=6, column=1, padx=10, sticky="w")

        tk.Label(info_frame, text="Thermocouple (°C):").grid(row=3, column=2, padx=10, sticky="w")
        tk.Label(info_frame, textvariable=self.temperature_thermocouple_var).grid(row=3, column=3, padx=10, sticky="w")
        tk.Label(info_frame, text="Temp. Approx (°C):", fg="maroon").grid(row=4, column=2, padx=10, sticky="w")
        tk.Label(info_frame, textvariable=self.temperature_approximate_var, fg="maroon").grid(row=4, column=3, padx=10, sticky="w")
        tk.Label(info_frame, text="Temp. Expected (°C):", fg="maroon").grid(row=5, column=2, padx=10, sticky="w")
        tk.Label(info_frame, textvariable=self.temperature_expected_var, fg="maroon").grid(row=5, column=3, padx=10, sticky="w")

        # Frame for IR correction
        ir_frame = tk.Frame(controls_frame)
        ir_frame.pack(pady=5)
        tk.Label(ir_frame, text="Corrective temperature IR (°C):").pack(side=tk.LEFT, padx=10)
        self.spinbox_temperature_ir = tk.Spinbox(ir_frame, from_=-1000, to=1000, increment=1, 
                                              textvariable=self.temperature_ir_var, width=5)
        self.spinbox_temperature_ir.pack(side=tk.LEFT, padx=10)
        tk.Button(ir_frame, text="SET", command=set_temperature_ir).pack(side=tk.LEFT, padx=10)

        # === Plot frame (lower part) ===
        plot_frame = tk.Frame(self.root)
        plot_frame.pack(pady=(0, 10), padx=10, fill=tk.BOTH, expand=True)
        self.temp_plot = TemperaturePlot(plot_frame)

        # Initialize LED indicator
        self.led_indicator = LEDIndicator(plot_frame)
        self.led_indicator.place(relx=0.95, rely=0.05, anchor="ne")
        self.led_indicator.configure(bg="white")
        self.led_indicator.configure(width=2)
        self.led_indicator.configure(height=2)

        # FINISH button at the bottom of controls frame
        tk.Button(controls_frame, text="FINISH", command=stop_program).pack(pady=(10, 10))

    def get_initial_time_var(self) -> Optional[tk.StringVar]:
        """Zwraca zmienną przechowującą początkowy czas."""
        return self.initial_time_var

    def get_temp_plot(self):
        """Zwraca obiekt wykresu temperatury."""
        return self.temp_plot

    def get_progress_bar(self) -> Optional[ttk.Progressbar]:
        """Zwraca pasek postępu."""
        return self.progress_bar

    def get_led_indicator(self):
        """Zwraca wskaźnik LED."""
        return self.led_indicator

    def get_curve_description_var(self) -> tk.StringVar:
        """Zwraca zmienną przechowującą opis krzywej."""
        return self.curve_description_var

    def get_spinbox_temperature_ir(self):
        """Zwraca referencję do spinboxa temperatury IR."""
        return self.spinbox_temperature_ir 

    def update_time(self, set_initial_time):
        """Aktualizuje czas na podstawie wartości z kontrolek."""
        try:
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())
            
            # Sprawdź poprawność wartości
            if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                raise ValueError("Nieprawidłowa wartość czasu")
            
            # Utwórz string czasu w formacie HH:MM
            time_str = f"{hours:02d}:{minutes:02d}"
            
            print(f"Ustawiono czas z kontrolek: {time_str}")
            
            # Aktualizuj zmienne czasu
            self.initial_time_var.set(time_str)
            
            # Wywołaj set_initial_time
            set_initial_time()
            
        except Exception as e:
            print(f"Błąd przy aktualizacji czasu: {e}")
            
    def reset_time(self, set_initial_time):
        """Resetuje czas do 00:00."""
        self.hours_var.set("00")
        self.minutes_var.set("00")
        self.initial_time_var.set("00:00")
        set_initial_time()
            
    def update_time_from_seconds(self, seconds):
        """Aktualizuje kontrolki czasu na podstawie wartości w sekundach."""
        try:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            
            self.hours_var.set(f"{hours:02d}")
            self.minutes_var.set(f"{minutes:02d}")
            
        except Exception as e:
            print(f"Błąd przy aktualizacji czasu: {e}") 