import time
import spidev

class Thermocouple:
    corrections = {
        300: 0,
        500: 0
    }

    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0, 1)
        self.spi.max_speed_hz = 50000
        self.last_valid_temperature = None

    def read_max31855(self):
        raw_data = self.spi.xfer2([0x00, 0x00, 0x00, 0x00])
        raw_value = (raw_data[0] << 24) | (raw_data[1] << 16) | (raw_data[2] << 8) | raw_data[3]
        
        # Sprawdzenie błędów
        if raw_value & 0x07:  # Jeśli są ustawione bity błędu, ignorujemy odczyt
            print("Błąd odczytu termopary! Zwracam ostatnią poprawną temperaturę.")
            return 0

        # Wydobycie temperatury w °C
        temp_raw = (raw_value >> 18) & 0x3FFF  # 14-bitowa temperatura
        if temp_raw & 0x2000:  # Sprawdzenie bitu znaku (dla liczb ujemnych)
            temp_raw -= 0x4000  # Uzupełnienie do dwóch

        temperature = temp_raw * 0.25  # MAX31855 używa kroku 0.25°C

        # Korekcja temperatury
        for key in sorted(self.corrections.keys(), reverse=True):
            if temperature > key:
                temperature += self.corrections[key]
                break
        
        self.last_valid_temperature = temperature  # Zapisujemy ostatnią poprawną temperaturę
        return temperature

