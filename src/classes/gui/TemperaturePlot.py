import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import numpy as np
from typing import List, Optional

class TemperaturePlot:
    def __init__(self, parent_frame):
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.ax.set_title("Temperature Profile")
        self.ax.set_xlabel("Time (HH:MM)")
        self.ax.set_ylabel("Temperature (°C)")

        # Lines for expected and actual temperature        
        self.line_actual, = self.ax.plot([], [], 'b-', label='Actual')
        # Line for the entire profile
        self.line_profile, = self.ax.plot([], [], 'g:', label='Profile')
        # Vertical line for current point
        self.line_current = self.ax.axvline(x=0, color='r', linestyle='-', linewidth=2, label='Current point', picker=5)

        # Ustawienie formatera osi X
        def time_formatter(x, pos):
            # Pobierz aktualną godzinę
            current_hour = time.localtime().tm_hour
            current_minute = time.localtime().tm_min
            
            # Konwertuj sekundy na godziny i minuty
            total_seconds = int(x)
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            
            # Dodaj aktualną godzinę
            target_hour = (current_hour + hours) % 24
            target_minute = (current_minute + minutes) % 60
            if current_minute + minutes >= 60:
                target_hour = (target_hour + 1) % 24
            
            return f"{target_hour:02d}:{target_minute:02d}"
        
        self.ax.xaxis.set_major_formatter(plt.FuncFormatter(time_formatter))

        self.ax.legend()
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Dane do wykresu
        self.time_data = []
        self.temp_actual_data = []
        self.profile_times = []
        self.profile_temps = []

        # Zmienne do przeciągania linii
        self.dragging = False
        self.drag_start_x = 0
        self.drag_current_x = 0

        # Zmienne do optymalizacji wykresu
        self.max_points = 1000  # Maksymalna liczba punktów na wykresie
        self.last_draw_time = 0  # Czas ostatniego rysowania
        self.draw_interval = 0.1  # Interwał rysowania w sekundach
        self.last_scale_time = 0  # Czas ostatniego skalowania
        self.scale_interval = 1.0  # Interwał skalowania w sekundach

        # Podłącz obsługę zdarzeń myszy
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('axes_enter_event', self.on_axes_enter)
        self.canvas.mpl_connect('axes_leave_event', self.on_axes_leave)

        # Tworzenie gradientu temperatury barwowej
        self.gradient = np.linspace(0, 1, 100).reshape(1, -1)
        self.gradient = np.vstack((self.gradient, self.gradient))
        
        # Inicjalizacja gradientu
        self.gradient_image = self.ax.imshow(
            self.gradient,
            aspect='auto',
            extent=[0, 1, 0, 1],
            alpha=0.2,
            cmap='hot',
            origin='lower'
        )
        self.gradient_image.set_visible(False)
        
        # Ustawienie zakresu osi
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)

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
        self.line_actual.set_data([], [])
        
        # Aktualizuj wykres
        actual = float(temperature_approximate_var.get())
        self.update_plot(xdata, actual)
        
        # Aktualizuj etykiety czasu
        update_time()
        
        print(f"Ustawiono czas z linii: {xdata} sekund ({hours:02}:{minutes:02})")

    def update_plot(self, elapsed_time, actual_temp):
        """Aktualizuje wykres z nowymi danymi."""
        try:
            # Dodaj nowe dane
            self.time_data.append(elapsed_time)
            self.temp_actual_data.append(actual_temp)
            self.ax.plot(self.time_data, self.temp_actual_data)
            
            # Aktualizuj pionową linię czasu
            max_temp = max(self.temp_actual_data)
            self.line_current.set_data([elapsed_time, elapsed_time], [0, max_temp])
          
            # Aktualizuj gradient
            if self.temp_actual_data:
                min_temp = min(self.temp_actual_data)
                max_temp = max(self.temp_actual_data)
                temp_range = max_temp - min_temp if max_temp > min_temp else 1
                
                # Aktualizuj zakres gradientu
                self.gradient_image.set_extent([0, len(self.temp_actual_data), min_temp, max_temp])
                self.gradient_image.set_visible(True)
            
            # Aktualizuj zakres osi
            if self.temp_actual_data:
                self.ax.set_xlim(0, len(self.temp_actual_data))
                self.ax.set_ylim(min(self.temp_actual_data) - 50, max(self.temp_actual_data) + 50)
            
        except Exception as e:
            print(f"Błąd przy aktualizacji wykresu: {e}")

    def draw_expected_profile(self, schedule):
        """Rysuje cały oczekiwany profil temperatury na podstawie harmonogramu."""
        # Sprawdź czy schedule zawiera klucz 'points'
        if not isinstance(schedule, dict) or 'points' not in schedule:
            print("Nieprawidłowy format harmonogramu")
            return
        
        # Konwersja godzin na sekundy
        schedule_seconds = {}
        for point in schedule['points']:
            time_str = point['time']
            hours, minutes = map(int, time_str.split(':'))
            seconds = hours * 3600 + minutes * 60
            try:
                schedule_seconds[seconds] = float(point['temperature'])
            except (ValueError, TypeError):
                print(f"Błąd konwersji temperatury na float: {point['temperature']}")
                continue
        
        if not schedule_seconds:
            print("Brak prawidłowych punktów w harmonogramie")
            return
            
        self.profile_times = sorted(schedule_seconds.keys())
        self.profile_temps = [schedule_seconds[t] for t in self.profile_times]

        # Ustawienie danych dla linii profilu
        self.line_profile.set_data(self.profile_times, self.profile_temps)

        # Ustawienie limitów osi Y na podstawie profilu + margines
        if self.profile_temps:
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
        self.line_actual.set_data([], [])
        if hasattr(self, 'line_current'):
            self.line_current.remove()
            self.line_current = self.ax.axvline(x=0, color='r', linestyle='-', linewidth=2, picker=5)

        self.ax.legend()
        self.canvas.draw()
        self.canvas.flush_events()
        self.canvas_widget.update_idletasks()
        self.canvas_widget.update() 