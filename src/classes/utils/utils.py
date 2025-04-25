from typing import Dict, Any, List
import time
import csv
import lgpio
import os

def time_to_seconds(time_str: str) -> int:
    """Konwertuje czas w formacie HH:MM na sekundy."""
    try:
        hours, minutes = map(int, time_str.split(':'))
        return hours * 3600 + minutes * 60
    except ValueError:
        return 0

def seconds_to_time(seconds: int) -> str:
    """Konwertuje sekundy na czas w formacie HH:MM:SS."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def write_data(file, data: List[Any]) -> None:
    """Zapisuje dane do pliku CSV."""
    try:
        writer = csv.writer(file)
        writer.writerow(data)
        file.flush()
    except Exception as e:
        print(f"Błąd podczas zapisywania danych: {e}")

def setup_gpio() -> int:
    """Inicjalizuje GPIO i zwraca uchwyt."""
    try:
        h = lgpio.gpiochip_open(0)
        return h
    except Exception as e:
        print(f"Błąd podczas inicjalizacji GPIO: {e}")
        return -1

def stop_program(h: int, ssr: Any, root: Any, file: Any) -> None:
    """Zatrzymuje program i zamyka wszystkie zasoby."""
    try:
        # Wyłącz SSR
        ssr.off()
        
        # Zamknij plik CSV
        if file:
            file.close()
        
        # Zamknij GPIO
        if h >= 0:
            lgpio.gpiochip_close(h)
        
        # Zamknij okno główne
        if root:
            root.quit()
            root.destroy()
        
        # Wymuś zamknięcie procesu
        os._exit(0)
    except Exception as e:
        print(f"Błąd podczas zamykania programu: {e}")
        os._exit(0)

def clear_inputs(h: int) -> None:
    """Czyści wszystkie wejścia GPIO."""
    try:
        # Wyczyść wszystkie wejścia GPIO
        for pin in range(0, 28):
            lgpio.gpio_claim_input(h, pin)
    except Exception as e:
        print(f"Błąd podczas czyszczenia wejść GPIO: {e}")

def set_inputs(h: int, pins: List[int]) -> None:
    """Ustawia podane piny jako wejścia GPIO."""
    try:
        for pin in pins:
            lgpio.gpio_claim_input(h, pin)
    except Exception as e:
        print(f"Błąd podczas ustawiania wejść GPIO: {e}")

def set_temperature_ir(temperature_ir_var: Any, spinbox: Any) -> None:
    """Ustawia temperaturę korekcyjną IR."""
    try:
        temperature_ir = float(spinbox.get())
        temperature_ir_var.set(temperature_ir)
    except ValueError:
        print("Nieprawidłowa wartość temperatury IR")

def update_temperature(state: Any) -> None:
    """Aktualizuje odczyty temperatury."""
    try:
        if not state.temperature_sensor:
            print("Brak czujnika temperatury")
            return
            
        # Odczytaj temperaturę z czujnika
        temperature = state.temperature_sensor.read_max31855()
        
        # Zastosuj korektę IR
        try:
            temperature_ir = float(state.temperature_ir_var.get() or 0)
            temperature += temperature_ir
        except (ValueError, AttributeError):
            print("Błąd podczas odczytu temperatury IR")
            temperature_ir = 0
        
        # Aktualizuj zmienne Tkinter
        if state.temperature_approximate_var:
            state.temperature_approximate_var.set(f"{temperature:.1f}")
        
        # Oblicz oczekiwaną temperaturę na podstawie harmonogramu
        if state.temperature_schedule and 'points' in state.temperature_schedule:
            expected_temp = 0
            for point in state.temperature_schedule['points']:
                time_str = point['time']
                time_sec = time_to_seconds(time_str)
                if time_sec <= state.elapsed_time:
                    expected_temp = point['temperature']
                else:
                    break
            if state.temperature_expected_var:
                state.temperature_expected_var.set(f"{expected_temp:.1f}")
    except Exception as e:
        print(f"Błąd podczas aktualizacji temperatury: {e}")

def update_pzem_data(pzem: Any, voltage_var: Any, current_var: Any, 
                    power_var: Any, energy_var: Any, freq_var: Any, 
                    cycle_var: Any) -> None:
    """Aktualizuje dane z miernika PZEM-004T."""
    try:
        if not pzem:
            print("Brak miernika PZEM-004T")
            return
            
        # Odczytaj dane z miernika
        voltage = pzem.voltage()
        current = pzem.current()
        power = pzem.power()
        energy = pzem.energy()
        frequency = pzem.frequency()
        power_factor = pzem.power_factor()
        
        # Aktualizuj zmienne Tkinter
        if voltage_var:
            voltage_var.set(f"{voltage:.1f}")
        if current_var:
            current_var.set(f"{current:.1f}")
        if power_var:
            power_var.set(f"{power:.1f}")
        if energy_var:
            energy_var.set(f"{energy:.1f}")
        if freq_var:
            freq_var.set(f"{frequency:.1f}")
        if cycle_var:
            cycle_var.set(f"{power_factor:.1f}")
    except Exception as e:
        print(f"Błąd podczas odczytu danych z PZEM-004T: {e}")

def update_time(elapsed_time: float, temperature_schedule: Dict[str, Any], 
                elapsed_time_var: Any, remaining_time_var: Any, 
                final_time_var: Any, progress_var: Any, 
                progress_bar: Any, progres_var_percent: Any,
                add_time: float, state: Any) -> None:
    """Aktualizuje etykiety czasu i postępu."""
    hours, remainder = divmod(int(elapsed_time), 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
    elapsed_time_var.set(time_str)

    # Oblicz pozostały czas na podstawie harmonogramu
    if temperature_schedule and 'points' in temperature_schedule:
        # Znajdź maksymalny czas w harmonogramie
        max_time = 0
        for point in temperature_schedule['points']:
            time_str = point['time']
            hours, minutes = map(int, time_str.split(':'))
            seconds = hours * 3600 + minutes * 60
            max_time = max(max_time, seconds)
            
        remaining_time = max(0, max_time - elapsed_time)
    else:
        remaining_time = 0
        max_time = 0
    
    hours, remainder = divmod(int(remaining_time), 3600)
    minutes, seconds = divmod(remainder, 60)
    remaining_time_var.set(f"{hours:02}:{minutes:02}:{seconds:02}") 

    # Oblicz postęp
    progress = (elapsed_time / max_time) * 100 if max_time > 0 else 0
    progress_var.set(progress)  # Aktualizuj wartość paska postępu
    if progress_bar:  # Sprawdź czy progress_bar istnieje
        progress_bar.update()  # Wymuś odświeżenie paska postępu

    # Oblicz przewidywany czas zakończenia
    final_time = time.strftime("%H:%M:%S", time.localtime(time.time() + remaining_time + add_time))
    final_time_var.set(final_time)

    progres_var_percent.set(f"{progress:.2f}%")
    
    # Aktualizuj opis krzywej temperatury
    if hasattr(state, 'temperature_curves') and hasattr(state, 'curve_var'):
        curve_description = state.temperature_curves.get_curve_stage(state.curve_var.get(), time_str)
        if hasattr(state, 'curve_description_var'):
            state.curve_description_var.set(curve_description)

def update_plots(state: Any) -> None:
    """Aktualizuje wykresy temperatury."""
    try:
        if state.temp_plot:
            actual = float(state.temperature_approximate_var.get())
            expected = float(state.temperature_expected_var.get())
            max_time = max(state.temperature_schedule.keys()) * 3600
            if state.elapsed_time <= max_time:
                state.temp_plot.update_plot(state.elapsed_time, actual, expected)
                state.temp_plot.canvas.draw()
                state.temp_plot.canvas.flush_events()
    except Exception as e:
        print(f"Błąd podczas aktualizacji wykresu: {e}")

def update_temp_and_humidity(state: Any) -> None:
    """Aktualizuje odczyty temperatury i wilgotności z czujnika SHT31."""
    try:
        # Odczytaj temperaturę i wilgotność z czujnika
        temperature, humidity = state.sht31.measurements
        
        # Aktualizuj zmienne Tkinter
        state.temperature_var.set(f"{temperature:.1f}")
        state.humidity_var.set(f"{humidity:.1f}")
    except Exception as e:
        print(f"Błąd podczas odczytu temperatury i wilgotności: {e}")

def update_PID(state: Any, elapsed_time: float, temperature_schedule: Dict[str, Any]) -> None:
    """Aktualizuje sterowanie PID."""
    try:
        # Pobierz aktualną temperaturę
        current_temp = float(state.temperature_thermocouple_var.get())
        
        # Pobierz oczekiwaną temperaturę
        expected_temp = get_expected_temperature(temperature_schedule, elapsed_time)
        
        # Oblicz nowe sterowanie
        output = state.pid_controller.compute_power(current_temp)
        
        # Aktualizuj zmienną Tkinter
        if state.pid_output_var:
            state.pid_output_var.set(f"{output:.2f}")
            
        return output
    except Exception as e:
        print(f"Błąd podczas aktualizacji PID: {e}")
        return 0

def get_expected_temperature(temperature_schedule: Dict[str, Any], elapsed_time: float) -> float:
    """Oblicza oczekiwaną temperaturę na podstawie harmonogramu i upływającego czasu."""
    try:
        if not temperature_schedule or 'points' not in temperature_schedule:
            return 0.0
            
        expected_temp = 0.0
        for point in temperature_schedule['points']:
            time_str = point['time']
            time_sec = time_to_seconds(time_str)
            if time_sec <= elapsed_time:
                expected_temp = point['temperature']
            else:
                break
        return expected_temp
    except Exception as e:
        print(f"Błąd podczas obliczania oczekiwanej temperatury: {e}")
        return 0.0 