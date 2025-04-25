import time
import csv
import lgpio
from typing import Dict, Any, Tuple, Optional
from src.classes.controllers.PIDController import PIDController
from src.classes.config.Config import Config

def time_to_seconds(time_str: str) -> int:
    """Konwertuje czas w formacie hh:mm na sekundy."""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 3600 + minutes * 60

def seconds_to_time(seconds: int) -> str:
    """Konwertuje sekundy na czas w formacie hh:mm."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02}:{minutes:02}"

def setup_gpio():
    """Inicjalizacja GPIO."""
    try:
        h = lgpio.gpiochip_open(0)
        return h
    except Exception as e:
        print(f"Błąd przy otwieraniu GPIO: {e}")
        return None

def stop_program(h: int, ssr: Any, root: Any, file_handle: Any = None) -> None:
    """Zatrzymuje program i zamyka wszystkie zasoby."""
    try:
        # Wyłącz SSR
        ssr.off()
        
        # Zamknij plik CSV jeśli jest otwarty
        if file_handle:
            file_handle.close()
            
        # Zamknij GPIO
        lgpio.gpiochip_close(h)
        
        # Zamknij okno główne
        root.quit()
        root.destroy()
        
        print("Program został prawidłowo zamknięty")
    except Exception as e:
        print(f"Błąd przy zamykaniu programu: {e}")
    finally:
        # Wymuś zamknięcie wszystkich wątków i procesów
        import os
        import sys
        import signal
        
        # Wyślij sygnał SIGTERM do wszystkich procesów potomnych
        os.killpg(os.getpgid(0), signal.SIGTERM)
        
        # Wymuś zamknięcie procesu
        sys.exit(0)
        os._exit(0)

def clear_inputs(spinbox_impulse_prev: Any, spinbox_impulse_after: Any) -> Tuple[float, float]:
    """Czyści pola wejściowe."""
    spinbox_impulse_prev.delete(0, 'end')
    spinbox_impulse_prev.insert(0, '0')
    spinbox_impulse_after.delete(0, 'end')
    spinbox_impulse_after.insert(0, '0')
    return 0.0, 0.0

def set_inputs(spinbox_impulse_prev: Any, spinbox_impulse_after: Any) -> Tuple[float, float]:
    """Ustawia wartości z pól wejściowych."""
    off_delay = float(spinbox_impulse_prev.get())
    on_delay = float(spinbox_impulse_after.get())
    return off_delay, on_delay

def set_temperature_ir(spinbox_temperature_ir_var: Any, temperature_ir_var: Any, 
                      temperature_thermocouple_var: Any, temp_calc: Any) -> None:
    """Ustawia temperaturę IR."""
    temperature_ir_var.set(float(spinbox_temperature_ir_var.get()))
    temp_calc.update_ir_temperature(float(spinbox_temperature_ir_var.get()), 
                                  float(temperature_thermocouple_var.get()))

def update_pzem_data(pzem: Any, voltage_var: Any, current_var: Any, 
                    power_var: Any, energy_var: Any, freq_var: Any, 
                    cycle_var: Any) -> None:
    """Aktualizuje dane z PZEM-004T."""
    pzem.read_data()
    voltage_var.set(f"{pzem.get_voltage():.2f}")
    current_var.set(f"{pzem.get_current():.2f}")
    power_var.set(f"{pzem.get_power():.2f}")
    energy_var.set(f"{pzem.get_energy():}")
    freq_var.set(f"{pzem.get_frequency():.2f}")
    cycle_var.set(f"{round(1000/float(pzem.get_frequency()), 2):.2f}")

def update_temperature(thermocouple: Any, temp_calc: Any, 
                      temperature_thermocouple_var: Any, 
                      temperature_approximate_var: Any) -> None:
    """Aktualizuje odczyty temperatury."""
    temp_calc.update_thermocouple_temperature(thermocouple.read_max31855()) 
    temperature_thermocouple_var.set(f"{thermocouple.read_max31855():.2f}")    
    temperature_approximate_var.set(temp_calc.get_approximate_temperature())

def update_temp_and_humidity(i2c: Any, bottom_cover_temperature: Any, 
                           humidity: Any) -> None:
    """Aktualizuje odczyty temperatury i wilgotności."""
    sensor = adafruit_sht31d.SHT31D(i2c)
    bottom_cover_temperature.set(f"{sensor.temperature:.2f}")
    humidity.set(f"{sensor.relative_humidity:.2f}")

def update_time(elapsed_time: float, temperature_schedule: Dict[str, Any], 
                elapsed_time_var: Any, remaining_time_var: Any, 
                final_time_var: Any, progress_var: Any, 
                progress_bar: Any, progres_var_percent: Any,
                add_time: float, curve_description: str, curve_description_var: Any) -> None:
    """Aktualizuje etykiety czasu i postępu."""
    hours, remainder = divmod(int(elapsed_time), 3600)
    minutes, seconds = divmod(remainder, 60)
    elapsed_time_var.set(f"{hours:02}:{minutes:02}:{seconds:02}")

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
    
    hours, remainder = divmod(int(remaining_time), 3600)
    minutes, seconds = divmod(remainder, 60)
    remaining_time_var.set(f"{hours:02}:{minutes:02}:{seconds:02}") 

    # Oblicz postęp
    if max_time > 0:
        progress = (elapsed_time / max_time) * 100
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
    curve_description_var.set(curve_description + " " + final_time)

def write_data(file_handle: Any, data: Dict[str, Any]) -> None:
    """Zapisuje dane do pliku CSV."""
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

    # Jeśli plik jest nowy i pusty, dodaj nagłówek
    if file_handle.tell() == 0:
        writer.writeheader()

    writer.writerows([data])  # Zapisanie danych 

def update_PID(temperature_approximate_var: Any, impulse_after_var: Any, 
               config: Any, temperature_curves: Any, curve_var: Any, 
               elapsed_time: float) -> int:
    """Aktualizuje sterowanie PID."""
    setpoint = get_expected_temperature(temperature_curves, curve_var, elapsed_time)
    pid = PIDController(setpoint, 
                       Kp=config.get_pid_value('Kp'), 
                       Ki=config.get_pid_value('Ki'), 
                       Kd=config.get_pid_value('Kd'))
    on_delay = int(pid.compute_power(float(temperature_approximate_var.get())))
    impulse_after_var.set(on_delay)
    return on_delay

def get_expected_temperature(temperature_curves: Any, curve_var: Any, 
                           elapsed_time: float) -> float:
    """Zwraca oczekiwaną temperaturę dla aktualnego czasu w wybranej krzywej."""
    # Konwertuj czas na format HH:MM:SS
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
    
    # Pobierz temperaturę z klasy TemperatureCurves
    temperature = temperature_curves.get_expected_temperature(curve_var.get(), time_str)
    
    if temperature is None:
        return 0.0  # Domyślna wartość w przypadku błędu
        
    return temperature 