import lgpio
import time

# Konfiguracja pinów
CHIP = 0  # Użyj domyślnego chipa GPIO
CONTROL_PIN = 24  # GPIO18 (PWM)
FREQUENCY = 5

# Otwórz połączenie z chipem GPIO
h = lgpio.gpiochip_open(CHIP)

# Ustaw pin jako wyjście
lgpio.gpio_claim_output(h, CONTROL_PIN)

try:
    # Pytanie użytkownika o moc
    while True:
        try:
            duty_cycle = int(input("Podaj moc (0-100%): "))
            if 0 <= duty_cycle <= 100:
                break
            else:
                print("Moc musi być w zakresie 0-100.")
        except ValueError:
            print("To nie jest prawidłowa liczba.")

    # Ustawienie wybranej mocy
    print(f"Ustawiam moc na {duty_cycle}%...")
    lgpio.tx_pwm(h, CONTROL_PIN, FREQUENCY, duty_cycle)  # Częstotliwość 100 Hz, wypełnienie duty_cycle%

    # Czekaj na przerwanie programu
    print("Naciśnij Ctrl+C, aby zakończyć.")
    while True:
        time.sleep(1)  # Utrzymuj moc, aż program zostanie przerwany

except KeyboardInterrupt:
    print("Przerywanie programu...")

# Zatrzymanie PWM i zamknięcie połączenia
lgpio.tx_pwm(h, CONTROL_PIN, FREQUENCY, 0)  # Wyłącz PWM
lgpio.gpiochip_close(h)
print("Program zakończony, moc wyłączona.")
