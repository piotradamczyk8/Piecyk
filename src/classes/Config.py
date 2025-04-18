import configparser
import os
from typing import Any, Dict

class Config:
    def __init__(self, config_file: str = "config.ini"):
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self._load_config()

    def _load_config(self) -> None:
        """Wczytuje konfigurację z pliku."""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Plik konfiguracyjny {self.config_file} nie istnieje")
        
        self.config.read(self.config_file)

    def get(self, section: str, option: str, fallback: Any = None) -> Any:
        """Pobiera wartość z konfiguracji."""
        return self.config.get(section, option, fallback=fallback)

    def getint(self, section: str, option: str, fallback: int = None) -> int:
        """Pobiera wartość całkowitą z konfiguracji."""
        return self.config.getint(section, option, fallback=fallback)

    def getfloat(self, section: str, option: str, fallback: float = None) -> float:
        """Pobiera wartość zmiennoprzecinkową z konfiguracji."""
        return self.config.getfloat(section, option, fallback=fallback)

    def getboolean(self, section: str, option: str, fallback: bool = None) -> bool:
        """Pobiera wartość logiczną z konfiguracji."""
        return self.config.getboolean(section, option, fallback=fallback)

    def get_section(self, section: str) -> Dict[str, str]:
        """Pobiera całą sekcję konfiguracji jako słownik."""
        if section not in self.config:
            return {}
        return dict(self.config[section])

    def set(self, section: str, option: str, value: Any) -> None:
        """Ustawia wartość w konfiguracji."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][option] = str(value)

    def save(self) -> None:
        """Zapisuje konfigurację do pliku."""
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    def reload(self) -> None:
        """Przeładowuje konfigurację z pliku."""
        self._load_config() 