import time
from src.classes.utils.utils import time_to_seconds, update_time
from src.classes.utils.utils import set_temperature_ir

class GUIController:
    def __init__(self, state):
        """Inicjalizacja kontrolera GUI.
        
        Args:
            state: Obiekt GlobalState zawierający stan aplikacji
        """
        self.state = state

    def set_temperature_schedule(self, curve_tk_var):
        """Ustawia harmonogram temperatury na podstawie wybranej krzywej."""
        selected_curve_name = curve_tk_var.get()

        # Pobierz harmonogram z klasy TemperatureCurves
        self.state.temperature_schedule = self.state.temperature_curves.get_curve(selected_curve_name)
        if self.state.temperature_schedule is None:
            print(f"Nie znaleziono krzywej: {selected_curve_name}")
            return

        print(f"Wybrano krzywą: {selected_curve_name}")
        if self.state.temp_plot:
            # Resetuj czas przy zmianie harmonogramu
            self.state.elapsed_time = self.state.add_time
            self.state.start_time = time.time() - self.state.add_time
            
            # Wyczyść dane wykresu
            self.state.temp_plot.time_data = []
            self.state.temp_plot.temp_actual_data = []
            self.state.temp_plot.line_actual.set_data([], [])
            self.state.temp_plot.line_current.set_data([], [])
            
            # Narysuj nowy profil
            self.state.temp_plot.draw_expected_profile(self.state.temperature_schedule)
            
            # Aktualizuj wykres z początkowymi wartościami
            actual = float(self.state.temperature_approximate_var.get())
            self.state.temp_plot.update_plot(self.state.elapsed_time, actual)
            
            # Odśwież wykres tylko raz
            self.state.temp_plot.canvas.draw()
            self.state.temp_plot.canvas.flush_events()

    def set_initial_time(self):
        """Ustawia początkowy czas dla harmonogramu."""
        try:
            # Pobierz wartość z pola tekstowego i przekonwertuj na sekundy
            time_str = f"{self.state.hours_var.get()}:{self.state.minutes_var.get()}"
            self.state.add_time = time_to_seconds(time_str)
            print(f"Ustawiono początkowy czas: {time_str} ({self.state.add_time} sekund)")
            
            # Aktualizuj start_time i elapsed_time
            self.state.start_time = time.time() - self.state.add_time
            self.state.elapsed_time = self.state.add_time
            
            # Aktualizuj wykres
            if self.state.temp_plot:
                # Wyczyść dane wykresu
                self.state.temp_plot.time_data = []
                self.state.temp_plot.temp_actual_data = []
                self.state.temp_plot.temp_expected_data = []
                self.state.temp_plot.line_actual.set_data([], [])
                
                # Narysuj nowy profil
                self.state.temp_plot.draw_expected_profile(self.state.temperature_schedule)
                
                # Aktualizuj wykres z początkowymi wartościami
                actual = float(self.state.temperature_approximate_var.get())
                self.state.temp_plot.update_plot(self.state.elapsed_time, actual)
               
                # Odśwież wykres tylko raz
                self.state.temp_plot.canvas.draw()
                self.state.temp_plot.canvas.flush_events()
                
                # Aktualizuj czerwoną linię czasu
                if hasattr(self.state.temp_plot, 'line_current'):
                    # Ustaw pełny zakres osi X
                    max_time = max(time_to_seconds(point['time']) for point in self.state.temperature_schedule['points'])
                    self.state.temp_plot.ax.set_xlim(0, max_time)
                    
                    # Aktualizuj formatowanie osi X z przesunięciem czasowym
                    def time_formatter(x, pos):
                        # Oblicz rzeczywisty czas (aktualny czas + przesunięcie)
                        current_time = time.time()
                        real_time = current_time + (x - self.state.elapsed_time)
                        
                        # Konwertuj na format HH:MM
                        time_struct = time.localtime(real_time)
                        return f"{time_struct.tm_hour:02d}:{time_struct.tm_min:02d}"
                    
                    self.state.temp_plot.ax.xaxis.set_major_formatter(time_formatter)
                    
                    # Aktualizuj czerwoną linię
                    self.state.temp_plot.line_current.set_data([self.state.elapsed_time, self.state.elapsed_time], 
                                                             [0, self.state.temp_plot.ax.get_ylim()[1]])
                    
                    # Odśwież wykres
                    self.state.temp_plot.canvas.draw()
                    self.state.temp_plot.canvas.flush_events()
            
            # Zawsze aktualizuj etykiety czasu i pasek postępu
            update_time(
                self.state.elapsed_time, 
                self.state.temperature_schedule, 
                self.state.elapsed_time_var, 
                self.state.remaining_time_var, 
                self.state.final_time_var, 
                self.state.progress_var, 
                self.state.progress_bar, 
                self.state.progres_var_percent, 
                self.state.add_time,
                self.state.curve_description_var.get() if self.state.curve_description_var else "",
                self.state.curve_description_var
            )
            
            # Odśwież interfejs
            self.state.root.update()
                
        except Exception as e:
            print(f"Błąd przy ustawianiu początkowego czasu: {e}")

    def set_temperature_ir_wrapper(self, gui_setup):
        """Wrapper dla funkcji set_temperature_ir z odpowiednimi argumentami."""
        set_temperature_ir(
            gui_setup.get_spinbox_temperature_ir(),
            self.state.temperature_ir_var,
            self.state.temperature_thermocouple_var,
            self.state.temp_calc
        ) 