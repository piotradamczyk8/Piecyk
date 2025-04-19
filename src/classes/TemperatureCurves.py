import csv
import os
from typing import Dict, List, Tuple

class TemperatureCurves:
    def __init__(self, curves_dir: str = "curves"):
        self.curves_dir = curves_dir
        self.curves: Dict[str, List[Tuple[float, float]]] = {}
        self.load_curves()

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
                (0, 30), (10800, 200), (14400, 400), (18000, 500),
                (21600, 600), (25200, 850), (26100, 850), (28800, 600),
                (32400, 500), (36000, 200), (39600, 30)
            ],
            "Stoneware": [
                (0, 30), (10800, 200), (14400, 400), (18000, 500),
                (21600, 600), (25200, 850), (26100, 850), (28800, 600),
                (32400, 500), (36000, 200), (39600, 30)
            ],
            "Porcelain": [
                (0, 30), (10800, 200), (14400, 400), (18000, 500),
                (21600, 600), (25200, 850), (26100, 850), (28800, 600),
                (32400, 500), (36000, 200), (39600, 30)
            ],
            "Raku": [
                (0, 30), (10800, 200), (14400, 400), (18000, 500),
                (21600, 600), (25200, 850), (26100, 850), (28800, 600),
                (32400, 500), (36000, 200), (39600, 30)
            ]
        }

        for name, curve in default_curves.items():
            self.save_curve(name, curve)

    def _load_curve(self, filepath: str) -> List[Tuple[float, float]]:
        """Wczytuje pojedynczą krzywą temperatury z pliku CSV."""
        curve = []
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 2:
                        try:
                            time = float(row[0])
                            temp = float(row[1])
                            curve.append((time, temp))
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Błąd podczas wczytywania pliku {filepath}: {e}")
        return curve

    def save_curve(self, name: str, curve: List[Tuple[float, float]]) -> None:
        """Zapisuje krzywą temperatury do pliku CSV."""
        if not os.path.exists(self.curves_dir):
            os.makedirs(self.curves_dir)

        filepath = os.path.join(self.curves_dir, f"{name}.csv")
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                for time, temp in curve:
                    writer.writerow([time, temp])
            self.curves[name] = curve
        except Exception as e:
            print(f"Błąd podczas zapisywania pliku {filepath}: {e}")

    def get_curve_names(self) -> List[str]:
        """Zwraca listę nazw dostępnych krzywych."""
        return list(self.curves.keys())

    def get_curve(self, name: str) -> List[Tuple[float, float]]:
        """Zwraca krzywą temperatury o podanej nazwie."""
        return self.curves.get(name, [])

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