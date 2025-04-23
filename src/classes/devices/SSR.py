import lgpio
from src.classes.Config import Config

class SSR:
    def __init__(self):
        """Inicjalizacja sterowania przekaźnikiem półprzewodnikowym."""
        self.config = Config()
        self.ssr_pin = self.config.get_gpio_pin("TRIAC_PIN")
        self.h = None
        self._open_gpio()

    def _open_gpio(self):
        """Otwiera połączenie GPIO jeśli nie jest otwarte."""
        if self.h is None:
            try:
                self.h = lgpio.gpiochip_open(0)
                lgpio.gpio_claim_output(self.h, self.ssr_pin)
            except Exception as e:
                print(f"Błąd przy otwieraniu GPIO: {e}")
                self.h = None

    def on(self):
        """Włącza SSR."""
        if self.h is None:
            self._open_gpio()
        if self.h is not None:
            lgpio.gpio_write(self.h, self.ssr_pin, 1)

    def off(self):
        """Wyłącza SSR."""
        if self.h is not None:
            try:
                lgpio.gpio_write(self.h, self.ssr_pin, 0)
                lgpio.gpiochip_close(self.h)
            except Exception as e:
                print(f"Błąd przy zamykaniu GPIO: {e}")
            finally:
                self.h = None

    def __del__(self):
        """Destruktor - wyłącza SSR i zamyka GPIO."""
        self.off() 