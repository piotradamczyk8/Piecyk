import spidev
import time

def test_slow_spi():
    print("Test MAX31855 z bardzo wolnym SPI")
    spi = spidev.SpiDev()
    spi.open(0, 1)
    spi.max_speed_hz = 10000  # Bardzo wolne 10kHz
    spi.mode = 0
    spi.bits_per_word = 8
    
    print("\nTestowanie z długimi przerwami...")
    for i in range(5):
        print(f"\nPróba {i+1}:")
        data = spi.xfer2([0x00, 0x00, 0x00, 0x00])
        print(f"Dane (hex): {[hex(x) for x in data]}")
        print(f"Dane (bin): {[bin(x) for x in data]}")
        time.sleep(1)  # Sekunda przerwy między odczytami
    
    spi.close()
    print("\nTest zakończony")

if __name__ == "__main__":
    test_slow_spi() 