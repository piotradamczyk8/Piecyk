import lgpio
from src.classes.Config import Config

class SSR:
    def __init__(self):
        """Inicjalizacja sterowania przekaźnikiem półprzewodnikowym."""
        self.config = Config()
        self.ssr_pin = self.config.get_gpio_pin("SSR_PIN")
        self.h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(self.h, self.ssr_pin)
        self.off()  # Upewnij się, że przekaźnik jest wyłączony na początku

    def on(self):
        """Włącza przekaźnik."""
        lgpio.gpio_write(self.h, self.ssr_pin, 1)

    def off(self):
        """Wyłącza przekaźnik."""
        lgpio.gpio_write(self.h, self.ssr_pin, 0)

    def __del__(self):
        """Zamyka połączenie GPIO przy usuwaniu obiektu."""
        try:
            self.off()  # Upewnij się, że przekaźnik jest wyłączony
            lgpio.gpiochip_close(self.h)
        except:
            pass  # Ignoruj błędy przy zamykaniu 