import time
import board
import busio
import numpy as np
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import matplotlib.pyplot as plt
from collections import deque


# Konfiguracja oscyloskopu
TIME_RANGE = 0.2  # Zakres czasu w sekundach (np. 2 sekundy)
VOLTAGE_RANGE = (-5, 5)  # Zakres napięcia na osi Y w woltach
SAMPLE_RATE = 860  # Liczba próbek na sekundę

# Inicjalizacja magistrali I2C i ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
ads.data_rate = SAMPLE_RATE  # Maksymalna częstotliwość próbkowania
chan = AnalogIn(ads, 0)

NUM_SAMPLES = int(TIME_RANGE * SAMPLE_RATE)  # Liczba próbek w całym zakresie czasowym
SAMPLE_INTERVAL = 1 / SAMPLE_RATE  # Interwał czasowy między próbkami

# Przygotowanie wykresu
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], '-b', lw=1, label="Przebieg")  # Linia reprezentująca ślad
dot, = ax.plot([], [], 'or', markersize=6, label="Kropka")  # Kropka
ax.set_xlim(0, TIME_RANGE)  # Zakres czasu (0 do TIME_RANGE)
ax.set_ylim(VOLTAGE_RANGE)  # Zakres napięcia (VOLTAGE_RANGE)
ax.set_xlabel("Czas (s)")
ax.set_ylabel("Napięcie (V)")
ax.set_title("Oscyloskop")
ax.grid(True)
ax.legend()

# Bufory na dane
time_buffer = deque(maxlen=NUM_SAMPLES)  # Bufor na czas
voltage_buffer = deque(maxlen=NUM_SAMPLES)  # Bufor na napięcia

# Funkcja do czyszczenia wykresu
def clear_plot():
    line.set_data([], [])  # Reset linii
    dot.set_data([], [])  # Reset kropki
    plt.draw()  # Odśwież wykres
    #ax.clear()

# Główna pętla odczytu
try:
    start_time = time.time()
    while True:
        # Odczyt napięcia
        current_time = time.time() - start_time

        # Oblicz pozycję w zakresie czasu
        time_mod = current_time % TIME_RANGE

        # Dodaj dane do buforów
        time_buffer.append(time_mod)
        voltage_buffer.append(voltage)

        # Aktualizacja wykresu
        if current_time < TIME_RANGE and voltage < 0.1:
            line.set_data(time_buffer, voltage_buffer)  # Rysuj ślad
            dot.set_data([time_mod], [voltage])  # Rysuj kropkę
            plt.draw()
            plt.pause(SAMPLE_INTERVAL)  # Próbkuj z odpowiednim interwałem

        # Gdy kropka osiągnie koniec zakresu czasu, wyczyść wykres
        if current_time > TIME_RANGE:  # Sprawdź, czy czas został zresetowany
            start_time = time.time()
            clear_plot()
            time_buffer.clear()  # Wyczyść bufor czasu
            voltage_buffer.clear()  # Wyczyść bufor napięć
except KeyboardInterrupt:
    print("Zatrzymano!")
finally:
    plt.ioff()
    plt.show()
