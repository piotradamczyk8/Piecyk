import spidev
import time

def test_miso():
    print("Test linii MISO (DO z MAX31855)")
    spi = spidev.SpiDev()
    spi.open(0, 1)
    spi.max_speed_hz = 100000
    spi.mode = 0
    spi.bits_per_word = 8
    
    print("\nTestowanie ciągłego odczytu przez 5 sekund...")
    start_time = time.time()
    non_zero_found = False
    
    while time.time() - start_time < 5:
        data = spi.xfer2([0x00])
        if data[0] != 0:
            non_zero_found = True
            print(f"Wykryto niezerowy odczyt: {hex(data[0])}")
        time.sleep(0.1)
    
    if not non_zero_found:
        print("\nNie wykryto żadnych niezerowych odczytów!")
        print("Sugerowane kroki:")
        print("1. Sprawdź czy linia DO nie jest zwarta do masy")
        print("2. Dodaj rezystor podciągający 10kΩ między DO a 3.3V")
        print("3. Sprawdź oscyloskopem stan linii DO")
    
    spi.close()

if __name__ == "__main__":
    test_miso() 