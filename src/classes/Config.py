import configparser
import os

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini')
        self.config.read(config_path)
    
    def get_gpio_pin(self, pin_name: str) -> int:
        """Pobiera numer pinu GPIO z konfiguracji."""
        return self.config.getint('GPIO', pin_name)
    
    def get_power_value(self, value_name: str) -> float:
        """Pobiera wartość z sekcji POWER."""
        return self.config.getfloat('POWER', value_name)
    
    def get_pid_value(self, value_name: str) -> float:
        """Pobiera wartość z sekcji PID."""
        return self.config.getfloat('PID', value_name)
    
    def get_gui_value(self, value_name: str) -> str:
        """Pobiera wartość z sekcji GUI."""
        return self.config.get('GUI', value_name)
    
    def get_csv_value(self, value_name: str) -> str:
        """Pobiera wartość z sekcji CSV."""
        return self.config.get('CSV', value_name) 