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
        # Lista możliwych lokalizacji pliku konfiguracyjnego
        possible_locations = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.ini'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini'),
            os.path.join(os.path.dirname(__file__), 'config.ini'),
            '/home/piotradamczyk/Projects/Piecyk/config.ini',
            'config.ini'
        ]
        
        # Próbuj wczytać plik z każdej lokalizacji
        for config_path in possible_locations:
            if os.path.exists(config_path):
                self.config.read(config_path)
                print(f"Znaleziono plik konfiguracyjny w: {config_path}")
                return
        
        # Jeśli nie znaleziono pliku, utwórz domyślną konfigurację
        print("Nie znaleziono pliku konfiguracyjnego, używam domyślnych wartości")
        self.config['GPIO'] = {'SSR_PIN': '24'}
        self.config['POWER'] = {
            'FREQ': '50',
            'HALF_CYCLE': '0.01',
            'POWER': '1',
            'DELAY': '0.01',
            'MAX_TIME_ON': '100'
        }
        self.config['PID'] = {
            'Kp': '320',
            'Ki': '160',
            'Kd': '8'
        }
        self.config['GUI'] = {
            'DEFAULT_CURVE': 'Bisquit',
            'WINDOW_WIDTH': '900',
            'WINDOW_HEIGHT': '1000'
        }
        self.config['CSV'] = {
            'ENCODING': 'utf-8',
            'NEWLINE': ''
        }
    
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