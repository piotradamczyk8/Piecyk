import json
import os
from typing import Dict, List, Optional, Tuple

class TemperatureCurves:
    def __init__(self):
        self.curves_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'curves')
        self.curves: Dict[str, Dict] = {}
        self._load_all_curves()

    def _load_all_curves(self) -> None:
        """Wczytuje wszystkie krzywe z katalogu curves."""
        if not os.path.exists(self.curves_dir):
            os.makedirs(self.curves_dir)
            return

        for filename in os.listdir(self.curves_dir):
            if filename.endswith('.json'):
                curve_name = os.path.splitext(filename)[0]
                try:
                    with open(os.path.join(self.curves_dir, filename), 'r', encoding='utf-8') as f:
                        self.curves[curve_name] = json.load(f)
                except Exception as e:
                    print(f"Błąd podczas wczytywania krzywej {filename}: {e}")

    def get_curves(self) -> List[str]:
        """Zwraca listę dostępnych krzywych."""
        return list(self.curves.keys())

    def get_curve(self, name: str) -> Optional[Dict]:
        """Zwraca krzywą o podanej nazwie."""
        return self.curves.get(name)

    def _time_to_seconds(self, time_str: str) -> int:
        """
        Konwertuje czas w formacie HH:MM:SS lub HH:MM na sekundy.
        
        Args:
            time_str: Czas w formacie HH:MM:SS lub HH:MM
            
        Returns:
            Czas w sekundach
        """
        parts = time_str.split(':')
        if len(parts) == 2:  # Format HH:MM
            hours, minutes = map(int, parts)
            seconds = 0
        elif len(parts) == 3:  # Format HH:MM:SS
            hours, minutes, seconds = map(int, parts)
        else:
            raise ValueError(f"Nieprawidłowy format czasu: {time_str}")
        
        return hours * 3600 + minutes * 60 + seconds

    def _seconds_to_time(self, seconds: int) -> str:
        """
        Konwertuje sekundy na czas w formacie HH:MM:SS.
        
        Args:
            seconds: Czas w sekundach
            
        Returns:
            Czas w formacie HH:MM:SS
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def get_curve_points(self, name: str, time_str: str) -> Optional[float]:
        """Zwraca temperaturę dla danego czasu w krzywej.
        
        Args:
            name: Nazwa krzywej
            time_str: Czas w formacie HH:MM:SS lub HH:MM
            
        Returns:
            Temperatura w stopniach Celsjusza lub None jeśli krzywa nie istnieje
        """
        curve = self.get_curve(name)
        if not curve:
            return None
            
        # Konwertuj czas na sekundy
        time_seconds = self._time_to_seconds(time_str)
        
        # Znajdź najbliższy punkt czasowy
        closest_point = None
        min_diff = float('inf')
        
        for point in curve['points']:
            point_time = self._time_to_seconds(point['time'])
            diff = abs(point_time - time_seconds)
            if diff < min_diff:
                min_diff = diff
                closest_point = point
                
        if closest_point:
            return closest_point['temperature']
        return None

    def get_curve_stage(self, name: str, time_str: str) -> Optional[str]:
        """Zwraca nazwę etapu dla danego czasu w krzywej.
        
        Args:
            name: Nazwa krzywej
            time_str: Czas w formacie HH:MM:SS lub HH:MM
            
        Returns:
            Nazwa etapu lub None jeśli krzywa nie istnieje
        """
        curve = self.get_curve(name)
        if not curve:
            return None
            
        # Konwertuj czas na sekundy
        time_seconds = self._time_to_seconds(time_str)
        
        # Znajdź najbliższy punkt czasowy
        closest_point = None
        min_diff = float('inf')
        
        for point in curve['points']:
            point_time = self._time_to_seconds(point['time'])
            diff = abs(point_time - time_seconds)
            if diff < min_diff:
                min_diff = diff
                closest_point = point
                
        if closest_point:
            return closest_point['stage']
        return None

    def get_curve_stage_description(self, name: str, time_str: str) -> Optional[str]:
        """
        Zwraca opis aktualnego zakresu temperaturowego dla podanego czasu.
        
        Args:
            name: Nazwa krzywej
            time_str: Czas w formacie HH:MM:SS lub HH:MM
            
        Returns:
            Opis zakresu temperaturowego lub None jeśli krzywa nie istnieje
        """
        curve = self.get_curve(name)
        if not curve:
            return None

        # Konwertuj czas na sekundy
        time_seconds = self._time_to_seconds(time_str)

        # Znajdź najbliższy punkt czasowy
        closest_point = None
        min_diff = float('inf')

        for point in curve['points']:
            point_time = self._time_to_seconds(point['time'])
            diff = abs(point_time - time_seconds)
            
            if diff < min_diff:
                min_diff = diff
                closest_point = point

        if closest_point:
            temperature = self.get_curve_points(name, time_str)
            if temperature is not None:
                return f"{closest_point['stage']} ({temperature}°C)"
        
        return None

    def get_curve_duration(self, name: str) -> Optional[str]:
        """
        Zwraca całkowity czas trwania krzywej w formacie HH:MM:SS.
        
        Args:
            name: Nazwa krzywej
            
        Returns:
            Czas trwania w formacie HH:MM:SS lub None jeśli krzywa nie istnieje
        """
        curve = self.get_curve(name)
        if not curve or not curve['points']:
            return None

        # Znajdź największy czas w krzywej
        max_time = max(self._time_to_seconds(point['time']) for point in curve['points'])
        return self._seconds_to_time(max_time)

    def get_expected_temperature(self, name: str, time_str: str) -> Optional[float]:
        """Zwraca oczekiwaną temperaturę dla danego czasu w krzywej.
        
        Args:
            name: Nazwa krzywej
            time_str: Czas w formacie HH:MM:SS lub HH:MM
            
        Returns:
            Temperatura w stopniach Celsjusza lub None jeśli krzywa nie istnieje
        """
        curve = self.get_curve(name)
        if not curve:
            return None
            
        # Konwertuj czas na sekundy
        time_seconds = self._time_to_seconds(time_str)
        
        # Znajdź punkty do interpolacji
        points = curve['points']
        times = [self._time_to_seconds(p['time']) for p in points]
        temps = [p['temperature'] for p in points]
        
        # Jeśli czas jest poza zakresem, zwróć graniczne wartości
        if time_seconds <= times[0]:
            return temps[0]
        if time_seconds >= times[-1]:
            return temps[-1]
            
        # Znajdź przedział do interpolacji
        for i in range(len(times) - 1):
            if times[i] <= time_seconds <= times[i + 1]:
                # Interpolacja liniowa
                t1, t2 = times[i], times[i + 1]
                temp1, temp2 = temps[i], temps[i + 1]
                temperature = temp1 + (temp2 - temp1) * (time_seconds - t1) / (t2 - t1)
                return temperature
                
        return None 