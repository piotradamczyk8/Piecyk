import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import numpy as np
from typing import List, Optional, Dict
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from matplotlib.lines import Line2D

class TemperaturePlot:
    def __init__(self, parent_frame):
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.ax.set_title(f"Temperature Profile Bisquit")
        self.ax.set_xlabel("Time (HH:MM)")
        self.ax.set_ylabel("Temperature (°C)")

        # Inicjalizacja danych
        self.time_data = [0]
        self.temp_actual_data = [0]
        self.profile_times = []
        self.profile_temps = []
        
        # Inicjalizacja linii
        self._init_lines()
        
        # Okienko z informacjami
        self.info_box = Rectangle((0, 0), 0.1, 0.1, facecolor='white', edgecolor='black', alpha=0.8)
        self.ax.add_patch(self.info_box)
        self.info_text = self.ax.text(0, 0, '', fontsize=8, ha='left', va='bottom')
        self.info_box.set_visible(False)
        self.info_text.set_visible(False)

        # Tekst z aktualnymi wartościami
        self.current_values_text = self.ax.text(0, 0, '', fontsize=8, ha='left', va='bottom',
                                              bbox=dict(facecolor='white', edgecolor='black', alpha=0.8))
        self.current_values_text.set_visible(True)

        # Linie podziału i opisy sekcji
        self.section_lines = []
        self.section_texts = []
        self.sections = {}  # Słownik przechowujący informacje o sekcjach

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

        # Zmienne do przeciągania linii
        self.dragging = False
        self.drag_start_x = 0
        self.drag_current_x = 0

        # Zmienne do optymalizacji wykresu
        self.max_points = 1000  # Maksymalna liczba punktów na wykresie
        self.last_draw_time = 0  # Czas ostatniego rysowania
        self.draw_interval = 0.5  # Interwał rysowania w sekundach
        self.last_scale_time = 0  # Czas ostatniego skalowania
        self.scale_interval = 1.0  # Interwał skalowania w sekundach
        
        # Cache dla ostatnich wartości
        self.last_elapsed_time = 0
        self.last_actual_temp = 0
        self.last_target_temp = 0
        self.last_update_time = 0
        self.update_interval = 0.5  # Zwiększamy interwał do 500ms
        
        # Cache dla punktów profilu
        self.profile_points = None
        self.profile_colors = None
        self.profile_scatter = None

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

    def _init_lines(self):
        """Inicjalizuje linie wykresu z początkowymi danymi."""
        try:
            # Lines for expected and actual temperature        
            self.line_actual, = self.ax.plot(self.time_data, self.temp_actual_data, 'b-', label='Actual')
            # Line for the entire profile
            self.line_profile, = self.ax.plot([], [], 'g:', label='Profile')
            # Vertical line for current point
            self.line_current = self.ax.axvline(x=0, color='r', linestyle='-', linewidth=2, label='Current point', picker=5)
            
            # Ustaw początkowy zakres osi
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            
            # Inicjalizuj dane linii
            self.line_current.set_xdata([0])
            
        except Exception as e:
            print(f"Błąd przy inicjalizacji linii: {e}")

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
            self.line_current.set_xdata([xdata])
            
            # Znajdź najbliższą temperaturę docelową
            target_temp = 0
            for i in range(len(self.profile_times) - 1):
                if self.profile_times[i] <= xdata <= self.profile_times[i + 1]:
                    # Interpoluj temperaturę
                    t1, t2 = self.profile_times[i], self.profile_times[i + 1]
                    temp1, temp2 = self.profile_temps[i], self.profile_temps[i + 1]
                    target_temp = temp1 + (temp2 - temp1) * (xdata - t1) / (t2 - t1)
                    break
            
            # Znajdź najbliższą temperaturę rzeczywistą
            actual_temp = 0
            if self.time_data and self.temp_actual_data:
                for i in range(len(self.time_data) - 1):
                    if self.time_data[i] <= xdata <= self.time_data[i + 1]:
                        # Interpoluj temperaturę
                        t1, t2 = self.time_data[i], self.time_data[i + 1]
                        temp1, temp2 = self.temp_actual_data[i], self.temp_actual_data[i + 1]
                        actual_temp = temp1 + (temp2 - temp1) * (xdata - t1) / (t2 - t1)
                        break
            
            # Aktualizuj wyświetlane wartości
            self.update_current_values(xdata, target_temp, actual_temp)
            
            # Odśwież tylko linię i tekst
            self.ax.draw_artist(self.line_current)
            self.ax.draw_artist(self.current_values_text)
            self.canvas.blit(self.ax.bbox)

    def update_time_from_line(self, xdata):
        """Aktualizuje czas na podstawie pozycji linii."""
        try:
            if not hasattr(self, 'line_current') or self.line_current is None:
                self._init_lines()
            
            # Ogranicz wartość do zakresu wykresu
            xdata = max(0, min(xdata, max(self.profile_times)))
            
            # Aktualizuj czasy
            self.add_time = xdata
            self.elapsed_time = xdata
            self.start_time = time.time() - xdata
            
            # Aktualizuj pole tekstowe
            hours = int(xdata // 3600)
            minutes = int((xdata % 3600) // 60)
            self.initial_time_var.set(f"{hours:02}:{minutes:02}")
            
            # Resetuj dane wykresu z początkowym punktem
            self.time_data = [xdata]
            self.temp_actual_data = [float(self.temperature_approximate_var.get())]
            
            # Aktualizuj linię z rzeczywistą temperaturą
            if hasattr(self, 'line_actual') and self.line_actual is not None:
                self.line_actual.set_data(self.time_data, self.temp_actual_data)
            
            # Aktualizuj pionową linię czasu
            if hasattr(self, 'line_current') and self.line_current is not None:
                self.line_current.set_xdata([xdata])
            
            # Aktualizuj wykres
            actual = float(self.temperature_approximate_var.get())
            self.update_plot(xdata, actual)
            
            # Aktualizuj etykiety czasu
            self.update_time()
            
            print(f"Ustawiono czas z linii: {xdata} sekund ({hours:02}:{minutes:02})")
            
        except Exception as e:
            print(f"Błąd przy aktualizacji czasu z linii: {e}")
            # Dodatkowe informacje o błędzie
            print(f"xdata: {xdata}")
            print(f"time_data: {self.time_data}")
            print(f"temp_actual_data: {self.temp_actual_data}")
            print(f"profile_times: {self.profile_times}")

    def update_plot(self, elapsed_time, actual_temp):
        """Aktualizuje wykres z nowymi danymi."""
        try:
            current_time = time.time()
            
            # Sprawdź czy minął wystarczający czas od ostatniej aktualizacji
            if current_time - self.last_update_time < self.update_interval:
                return
                
            self.last_update_time = current_time
            
            # Sprawdź czy wartości się znacząco zmieniły
            if (abs(elapsed_time - self.last_elapsed_time) < 1 and 
                abs(actual_temp - self.last_actual_temp) < 0.1):
                return
                
            self.last_elapsed_time = elapsed_time
            self.last_actual_temp = actual_temp
            
            # Dodaj nowe dane
            self.time_data.append(elapsed_time)
            self.temp_actual_data.append(actual_temp)
            
            # Ogranicz liczbę punktów na wykresie
            if len(self.time_data) > self.max_points:
                self.time_data = self.time_data[-self.max_points:]
                self.temp_actual_data = self.temp_actual_data[-self.max_points:]
            
            # Aktualizuj linię z rzeczywistą temperaturą
            if hasattr(self, 'line_actual') and self.line_actual is not None:
                self.line_actual.set_data(self.time_data, self.temp_actual_data)
            
            # Aktualizuj tylko położenie X czerwonej linii
            if hasattr(self, 'line_current') and self.line_current is not None:
                self.line_current.set_xdata([elapsed_time])
            
            # Znajdź najbliższą temperaturę docelową
            target_temp = self._find_target_temp(elapsed_time)
            
            # Aktualizuj wyświetlane wartości tylko jeśli się znacząco zmieniły
            if abs(target_temp - self.last_target_temp) >= 0.1:
                self.last_target_temp = target_temp
                self.update_current_values(elapsed_time, target_temp, actual_temp)
            
            # Odśwież cały wykres
            self.canvas.draw()
            
        except Exception as e:
            print(f"Błąd przy aktualizacji wykresu: {e}")
            # Dodatkowe informacje o błędzie
            print(f"time_data: {self.time_data}")
            print(f"temp_actual_data: {self.temp_actual_data}")
            print(f"elapsed_time: {elapsed_time}")
            print(f"actual_temp: {actual_temp}")

    def _find_target_temp(self, elapsed_time):
        """Znajduje docelową temperaturę dla danego czasu."""
        if not self.profile_times:
            return 0
            
        idx = np.searchsorted(self.profile_times, elapsed_time)
        if idx > 0 and idx < len(self.profile_times):
            t1, t2 = self.profile_times[idx-1], self.profile_times[idx]
            temp1, temp2 = self.profile_temps[idx-1], self.profile_temps[idx]
            return temp1 + (temp2 - temp1) * (elapsed_time - t1) / (t2 - t1)
        elif idx == 0:
            return self.profile_temps[0]
        else:
            return self.profile_temps[-1]

    def temperature_to_color(self, temp):
        """Konwertuje temperaturę na kolor RGB.
        
        Kolory zmieniają się następująco:
        - 30°C: czarny (0, 0, 0)
        - 400°C: ciemny czerwony (0.5, 0, 0)
        - 800°C: pomarańczowy (1, 0.5, 0)
        - 1000°C: jasny pomarańczowy (1, 0.7, 0)
        - >1000°C: żółty (1, 1, 0)
        """
        # Normalizuj temperaturę do zakresu 0-1
        # Zakładamy, że temperatura zmienia się od 30 do 1200°C
        normalized_temp = min(max((temp - 30) / (1200 - 30), 0.0), 1.0)
        
        if normalized_temp < 0.33:  # 30-400°C
            # Od czarnego do ciemnego czerwonego
            r = normalized_temp * 1.5
            g = 0
            b = 0
        elif normalized_temp < 0.66:  # 400-800°C
            # Od ciemnego czerwonego do pomarańczowego
            r = 1
            g = (normalized_temp - 0.33) * 1.5
            b = 0
        else:  # 800-1200°C
            # Od pomarańczowego do żółtego
            r = 1
            g = 0.5 + (normalized_temp - 0.66) * 1.5
            b = 0
            
        return (r, g, b)

    def draw_expected_profile(self, schedule):
        """Rysuje profil temperatury z harmonogramu."""
        try:
            if not schedule or 'points' not in schedule:
                return
                
            # Wyczyść poprzedni profil
            self.profile_times = []
            self.profile_temps = []
            
            # Zbierz punkty z harmonogramu
            for point in schedule['points']:
                time_str = point['time']
                hours, minutes = map(int, time_str.split(':'))
                seconds = hours * 3600 + minutes * 60
                temp = float(point['temperature'])
                
                self.profile_times.append(seconds)
                self.profile_temps.append(temp)
            
            # Przygotuj wszystkie punkty i kolory
            all_times = []
            all_temps = []
            all_colors = []
            
            # Ustaw początkowy zakres osi
            if self.profile_times:
                self.ax.set_xlim(0, max(self.profile_times))
                self.ax.set_ylim(0, max(self.profile_temps) * 1.1)
            
            # Oblicz liczbę punktów na podstawie stałej wartości
            POINTS_PER_HOUR = 3600  # Jeden punkt na sekundę
            
            for i in range(len(self.profile_times) - 1):
                time_range = self.profile_times[i + 1] - self.profile_times[i]
                points_per_segment = max(2, int(time_range))
                
                times = np.linspace(self.profile_times[i], self.profile_times[i + 1], points_per_segment)
                temps = np.linspace(self.profile_temps[i], self.profile_temps[i + 1], points_per_segment)
                
                all_times.extend(times)
                all_temps.extend(temps)
                all_colors.extend([self.temperature_to_color(temp) for temp in temps])
            
            # Dodaj ostatni punkt
            all_times.append(self.profile_times[-1])
            all_temps.append(self.profile_temps[-1])
            all_colors.append(self.temperature_to_color(self.profile_temps[-1]))
            
            # Zapisz punkty i kolory
            self.profile_points = np.column_stack((all_times, all_temps))
            self.profile_colors = all_colors
            
            # Usuń poprzedni scatter jeśli istnieje
            if self.profile_scatter is not None:
                self.profile_scatter.remove()
            
            # Narysuj wszystkie punkty na raz
            self.profile_scatter = self.ax.scatter(all_times, all_temps, c=all_colors, s=1, marker='.')
            
            # Odśwież cały wykres
            self.canvas.draw()
            
        except Exception as e:
            print(f"Błąd przy rysowaniu profilu: {e}")
            import traceback
            traceback.print_exc()

    def set_title(self, title: str):
        """Ustawia tytuł wykresu."""
        self.ax.set_title(title)
        self.canvas.draw()

    def add_section(self, start_time: int, end_time: int, name: str, description: str):
        """Dodaje nową sekcję na wykresie."""
        # Konwertuj czas na sekundy jeśli podano w formacie HH:MM
        if isinstance(start_time, str):
            hours, minutes = map(int, start_time.split(':'))
            start_time = hours * 3600 + minutes * 60
        if isinstance(end_time, str):
            hours, minutes = map(int, end_time.split(':'))
            end_time = hours * 3600 + minutes * 60

        # Dodaj linię podziału
        line = self.ax.axvline(x=end_time, color='gray', linestyle='--', alpha=0.5)
        self.section_lines.append(line)

        # Dodaj tekst z nazwą sekcji
        text = self.ax.text((start_time + end_time) / 2, self.ax.get_ylim()[1] * 0.95,
                           name, ha='center', va='top', fontsize=9,
                           bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
        self.section_texts.append(text)

        # Zapisz informacje o sekcji
        self.sections[end_time] = {
            'name': name,
            'description': description,
            'start_time': start_time,
            'end_time': end_time
        }

    def clear_sections(self):
        """Usuwa wszystkie sekcje z wykresu."""
        for line in self.section_lines:
            line.remove()
        for text in self.section_texts:
            text.remove()
        self.section_lines = []
        self.section_texts = []
        self.sections = {} 

    def update_current_values(self, current_time, target_temp, actual_temp):
        """Aktualizuje wyświetlane wartości przy czerwonej linii."""
        try:
            if not self.current_values_text:
                return
                
            # Konwertuj czas na format HH:MM
            hours = int(current_time // 3600)
            minutes = int((current_time % 3600) // 60)
            time_str = f"{hours:02d}:{minutes:02d}"
            
            # Formatuj tekst z wartościami
            text = f"Time: {time_str}\nTarget: {target_temp:.1f}°C\nActual: {actual_temp:.1f}°C"
            
            # Ustaw pozycję tekstu
            x_pos = current_time
            y_pos = max(target_temp, actual_temp) + 10  # 10 stopni powyżej wyższej temperatury
            
            # Ogranicz pozycję do zakresu wykresu
            x_lim = self.ax.get_xlim()
            y_lim = self.ax.get_ylim()
            x_pos = max(x_lim[0] + 0.05 * (x_lim[1] - x_lim[0]), 
                       min(x_lim[1] - 0.05 * (x_lim[1] - x_lim[0]), x_pos))
            y_pos = max(y_lim[0] + 0.05 * (y_lim[1] - y_lim[0]), 
                       min(y_lim[1] - 0.05 * (y_lim[1] - y_lim[0]), y_pos))
            
            # Aktualizuj tekst i pozycję
            self.current_values_text.set_text(text)
            self.current_values_text.set_position((x_pos, y_pos))
            
            # Odśwież cały wykres
            self.canvas.draw()
            
        except Exception as e:
            print(f"Błąd przy aktualizacji wartości: {e}") 