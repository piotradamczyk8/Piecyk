import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
PIN = 17

# Pobranie statusu pinu
try:
    state = GPIO.gpio_function(PIN)  # Sprawdza tryb GPIO
    if state == GPIO.IN:
        print(f"GPIO{PIN} jest ustawione jako WEJŚCIE (IN)")
    elif state == GPIO.OUT:
        print(f"GPIO{PIN} jest ustawione jako WYJŚCIE (OUT)")
    else:
        print(f"GPIO{PIN} jest w innym trybie ({state})")
except RuntimeError as e:
    print(f"Błąd: {e}")

GPIO.cleanup()
