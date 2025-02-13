import spidev
import time

# Inicjalizacja SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0 (SPI0_CS0)
spi.max_speed_hz = 50000  # Maksymalna prędkość SPI w Hz

# Funkcja ustawiająca wartość na rezystorze
def set_resistor(channel, value):
    """
    Ustawia wartość w wiperze dla wybranego kanału.
    
    :param channel: Numer kanału (0-3).
    :param value: Wartość w zakresie 0-255.
    """
    if not (0 <= channel <= 3):
        raise ValueError("Numer kanału musi być z zakresu 0-3.")
    if not (0 <= value <= 255):
        raise ValueError("Wartość musi być z zakresu 0-255.")

    command = [0b01000000 | (channel << 1), 0b00000001, value]  # Opcja zapisu do TR
    spi.xfer2(command)
    time.sleep(1)  # Krótka przerwa dla stabilizacji

# Przykładowe ustawienie
channel = 0  # Kanał 0
value =  255 # Środkowa wartość (50%)
set_resistor(channel, value)

# Zamknij SPI po zakończeniu
spi.close()
