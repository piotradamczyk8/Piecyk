import csv
import os
from typing import Dict, List, Tuple

class TemperatureCurves:
    def __init__(self, curves_dir: str = "curves"):
        self.curves_dir = curves_dir
        self.curves: Dict[str, List[Tuple[float, float, str]]] = {}
        self.load_curves()

    def _time_to_seconds(self, time_str: str) -> float:
        """Konwertuje czas w formacie HH:MM na sekundy."""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 3600 + minutes * 60
        except ValueError:
            return 0.0

    def _seconds_to_time(self, seconds: float) -> str:
        """Konwertuje sekundy na czas w formacie HH:MM."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours:02d}:{minutes:02d}"

    def load_curves(self) -> None:
        """Wczytuje wszystkie krzywe temperatury z plików CSV w katalogu curves."""
        if not os.path.exists(self.curves_dir):
            os.makedirs(self.curves_dir)
            # Tworzenie domyślnych krzywych jeśli katalog jest pusty
            if not os.listdir(self.curves_dir):
                self._create_default_curves()
            return

        for filename in os.listdir(self.curves_dir):
            if filename.endswith('.csv'):
                curve_name = os.path.splitext(filename)[0]
                self.curves[curve_name] = self._load_curve(os.path.join(self.curves_dir, filename))

    def _create_default_curves(self) -> None:
        """Tworzy domyślne krzywe temperatury."""
        default_curves = {
            "Bisquit": [
                ("00:00", 30, "Initial Heating"),
                ("03:00", 200, "Preheating"),
                ("04:00", 400, "Water Smoking"),
                ("05:00", 500, "Quartz Inversion"),
                ("06:00", 600, "Bisquit Firing"),
                ("07:00", 850, "Soaking"),
                ("07:15", 850, "Soaking"),
                ("08:00", 600, "Cooling"),
                ("09:00", 500, "Quartz Inversion"),
                ("10:00", 200, "Final Cooling"),
                ("11:00", 30, "Complete")
            ],
            "Bisquit_express": [
                ("00:00", 30, "Initial Heating"),
                ("02:00", 200, "Preheating"),
                ("03:00", 400, "Water Smoking"),
                ("04:00", 500, "Quartz Inversion"),
                ("05:00", 600, "Bisquit Firing"),
                ("06:00", 850, "Soaking"),
                ("06:15", 850, "Soaking"),
                ("07:00", 600, "Cooling"),
                ("08:00", 500, "Quartz Inversion"),
                ("09:00", 200, "Final Cooling"),
                ("10:00", 30, "Complete")
            ],
            "Glazing": [
                ("00:00", 30, "Initial Heating"),
                ("03:00", 200, "Preheating"),
                ("04:00", 400, "Water Smoking"),
                ("05:00", 500, "Quartz Inversion"),
                ("06:00", 600, "Glaze Firing"),
                ("07:00", 850, "Soaking"),
                ("07:15", 850, "Soaking"),
                ("08:00", 600, "Cooling"),
                ("09:00", 500, "Quartz Inversion"),
                ("10:00", 200, "Final Cooling"),
                ("11:00", 30, "Complete")
            ],
            "Glazing_perfect": [
                ("00:00", 30, "Initial Heating"),
                ("03:00", 200, "Preheating"),
                ("04:00", 400, "Water Smoking"),
                ("05:00", 500, "Quartz Inversion"),
                ("06:00", 600, "Glaze Firing"),
                ("07:00", 850, "Soaking"),
                ("07:15", 850, "Soaking"),
                ("08:00", 600, "Cooling"),
                ("09:00", 500, "Quartz Inversion"),
                ("10:00", 200, "Final Cooling"),
                ("11:00", 30, "Complete")
            ],
            "Glazing_express": [
                ("00:00", 30, "Initial Heating"),
                ("02:00", 200, "Preheating"),
                ("03:00", 400, "Water Smoking"),
                ("04:00", 500, "Quartz Inversion"),
                ("05:00", 600, "Glaze Firing"),
                ("06:00", 850, "Soaking"),
                ("06:15", 850, "Soaking"),
                ("07:00", 600, "Cooling"),
                ("08:00", 500, "Quartz Inversion"),
                ("09:00", 200, "Final Cooling"),
                ("10:00", 30, "Complete")
            ]
        }

        for name, curve in default_curves.items():
            # Konwersja czasu na sekundy przed zapisem
            curve_seconds = [(self._time_to_seconds(time), temp, stage) for time, temp, stage in curve]
            self.save_curve(name, curve_seconds)

    def _load_curve(self, filepath: str) -> List[Tuple[float, float, str]]:
        """Wczytuje pojedynczą krzywą temperatury z pliku CSV."""
        curve = []
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 3:
                        try:
                            time = float(row[0])
                            temp = float(row[1])
                            stage = row[2]
                            curve.append((time, temp, stage))
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Błąd podczas wczytywania pliku {filepath}: {e}")
        return curve

    def save_curve(self, name: str, curve: List[Tuple[float, float, str]]) -> None:
        """Zapisuje krzywą temperatury do pliku CSV."""
        if not os.path.exists(self.curves_dir):
            os.makedirs(self.curves_dir)

        filepath = os.path.join(self.curves_dir, f"{name}.csv")
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                for time, temp, stage in curve:
                    writer.writerow([time, temp, stage])
            self.curves[name] = curve
        except Exception as e:
            print(f"Błąd podczas zapisywania pliku {filepath}: {e}")

    def get_curve_names(self) -> List[str]:
        """Zwraca listę nazw dostępnych krzywych."""
        return list(self.curves.keys())

    def get_curve(self, name: str) -> List[Tuple[float, float, str]]:
        """Zwraca krzywą temperatury o podanej nazwie."""
        return self.curves.get(name, [])

    def get_curve_with_time_format(self, name: str) -> List[Tuple[str, float, str]]:
        """Zwraca krzywą temperatury o podanej nazwie z czasem w formacie HH:MM."""
        curve = self.get_curve(name)
        return [(self._seconds_to_time(time), temp, stage) for time, temp, stage in curve]

    def delete_curve(self, name: str) -> bool:
        """Usuwa krzywą temperatury o podanej nazwie."""
        if name in self.curves:
            filepath = os.path.join(self.curves_dir, f"{name}.csv")
            try:
                os.remove(filepath)
                del self.curves[name]
                return True
            except Exception as e:
                print(f"Błąd podczas usuwania pliku {filepath}: {e}")
        return False

    def get_expected_temperature(self, time: float) -> float:
        """Zwraca oczekiwaną temperaturę dla danego czasu."""
        if not self.curves:
            return 0.0

        # Pobierz pierwszą dostępną krzywą
        curve = next(iter(self.curves.values()))
        if not curve:
            return 0.0

        # Znajdź najbliższe punkty czasowe
        prev_time, prev_temp, _ = curve[0]
        for curr_time, curr_temp, _ in curve[1:]:
            if curr_time >= time:
                # Interpolacja liniowa
                if curr_time == prev_time:
                    return curr_temp
                ratio = (time - prev_time) / (curr_time - prev_time)
                return prev_temp + (curr_temp - prev_temp) * ratio
            prev_time, prev_temp = curr_time, curr_temp

        return prev_temp

    def get_selected_curve(self) -> str:
        """Zwraca nazwę aktualnie wybranej krzywej temperatury."""
        if not self.curves:
            return None
        # Zwróć pierwszą dostępną krzywą
        return next(iter(self.curves.keys()))

    def get_current_stage(self, elapsed_time: int) -> str:
        """Zwraca nazwę aktualnego etapu dla danego czasu."""
        if elapsed_time < 0:
            return "Nie rozpoczęto"
            
        # Pobierz aktualnie wybraną krzywą
        selected_curve = self.get_selected_curve()
        if not selected_curve:
            return "Brak wybranej krzywej"
            
        # Pobierz dane krzywej
        curve_data = self.curves.get(selected_curve, [])
        if not curve_data:
            return "Brak danych krzywej"
            
        # Znajdź aktualny etap
        for i in range(len(curve_data) - 1):
            current_time, _, current_stage = curve_data[i]
            next_time, _, _ = curve_data[i + 1]
            if current_time <= elapsed_time < next_time:
                return current_stage
                
        # Jeśli czas jest poza zakresem
        return "Zakończono" 