import time
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import matplotlib.pyplot as plt

# Inicjalizacja I²C i ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)

# Wybór kanału (np. A0)
chan = AnalogIn(ads, 0)

# Dane do wykresu
x_data = []
y_data = []

# Funkcja do aktualizacji wykresu
def update_plot():
    plt.clf()
    plt.plot(x_data, y_data)
    plt.title("Mikrooscyloskop - ADS1115")
    plt.xlabel("Czas (s)")
    plt.ylabel("Napięcie (V)")
    plt.grid()
    plt.pause(0.01)

# Główna pętla
start_time = time.time()
while True:
    try:
        voltage = chan.voltage
        elapsed_time = time.time() - start_time
        x_data.append(elapsed_time)
        y_data.append(voltage)

        # Zachowanie tylko ostatnich 100 punktów
        if len(x_data) > 100:
            x_data.pop(0)
            y_data.pop(0)

        # Aktualizacja wykresu
        update_plot()
        time.sleep(0.01)

    except KeyboardInterrupt:
        print("Zatrzymano!")
        break

plt.show()
