import json
import os
from typing import Dict, List, Optional, Tuple

class TemperatureCurves:
    def __init__(self):
        # Lista możliwych lokalizacji katalogu z krzywymi
        possible_locations = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'curves'),
            os.path.join(os.path.dirname(__file__), 'curves'),
            '/home/piotradamczyk/Projects/Piecyk/src/curves',
            'src/curves',
            'curves'
        ]
        
        # Znajdź pierwszy istniejący katalog
        self.curves_dir = None
        for location in possible_locations:
            if os.path.exists(location):
                self.curves_dir = location
                print(f"Znaleziono katalog z krzywymi w: {location}")
                break
        
        if self.curves_dir is None:
            print("Nie znaleziono katalogu z krzywymi")
            self.curves_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'curves')
            os.makedirs(self.curves_dir, exist_ok=True)
            print(f"Utworzono nowy katalog z krzywymi w: {self.curves_dir}")
        
        # Cache dla krzywych
        self._curves_cache = {}
        self._curves_names = None
        self._load_curves_names()

    def _load_curves_names(self) -> None:
        """Wczytuje tylko nazwy dostępnych krzywych."""
        if not os.path.exists(self.curves_dir):
            os.makedirs(self.curves_dir)
            self._curves_names = []
            return

        # Wczytaj tylko nazwy plików bez rozszerzenia
        self._curves_names = [
            os.path.splitext(filename)[0]
            for filename in os.listdir(self.curves_dir)
            if filename.endswith('.json')
        ]

    def _load_curve(self, name: str) -> Optional[Dict]:
        """Wczytuje pojedynczą krzywą z pliku tylko gdy jest potrzebna."""
        if name in self._curves_cache:
            return self._curves_cache[name]

        filename = f"{name}.json"
        filepath = os.path.join(self.curves_dir, filename)
        
        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                curve = json.load(f)
                # Konwertuj czasy na sekundy dla wszystkich punktów
                for point in curve['points']:
                    point['time_seconds'] = self._time_to_seconds(point['time'])
                self._curves_cache[name] = curve
                return curve
        except Exception as e:
            print(f"Błąd podczas wczytywania krzywej {filename}: {e}")
            return None

    @property
    def curves(self) -> List[str]:
        """Zwraca listę dostępnych krzywych."""
        return self._curves_names

    def get_curve(self, name: str) -> Optional[Dict]:
        """Zwraca krzywą o podanej nazwie, wczytując ją jeśli nie jest w cache."""
        return self._load_curve(name)

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
        times = [p['time_seconds'] for p in points]
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