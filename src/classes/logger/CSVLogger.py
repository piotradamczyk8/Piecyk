import csv
import time
from datetime import datetime

class CSVLogger:
    def __init__(self, curve_name, config):
        """Inicjalizacja loggera CSV.
        
        Args:
            curve_name (str): Nazwa krzywej wypalania
            config (Config): Obiekt konfiguracji
        """
        self.config = config
        self.filename = f"dane_{curve_name.lower()}_{datetime.now().strftime('%Y-%m-%d_%H%M')}.csv"
        self.file = None
        self.writer = None
        self.open_file()

    def open_file(self):
        """Otwiera plik CSV w trybie append z odpowiednimi parametrami."""
        self.file = open(
            self.filename,
            mode="a",
            newline=self.config.get_csv_value('NEWLINE'),
            encoding=self.config.get_csv_value('ENCODING')
        )
        self.writer = csv.writer(self.file)

    def write_data(self, data):
        """Zapisuje dane do pliku CSV.
        
        Args:
            data (list): Lista wartości do zapisania
        """
        if self.writer:
            self.writer.writerow(data)
            self.file.flush()  # Wymusza zapis do pliku

    def close(self):
        """Zamyka plik CSV."""
        if self.file:
            self.file.close()
            self.file = None
            self.writer = None

    def __del__(self):
        """Destruktor - zamyka plik jeśli jest otwarty."""
        self.close() 