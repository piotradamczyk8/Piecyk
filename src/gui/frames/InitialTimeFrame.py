import tkinter as tk
from tkinter import ttk

class InitialTimeFrame:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=5)
        
        # Zmienna dla czasu początkowego
        self.initial_time_var = tk.StringVar(value="01:00")
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Etykieta i pole tekstowe dla czasu początkowego
        tk.Label(self.frame, text="Initial Time (HH:MM):").grid(row=0, column=0, padx=5, sticky="w")
        self.time_entry = tk.Entry(self.frame, textvariable=self.initial_time_var, width=10)
        self.time_entry.grid(row=0, column=1, padx=5, sticky="w")
        
        # Przycisk SET
        self.set_button = tk.Button(self.frame, text="SET", command=self._on_set_clicked)
        self.set_button.grid(row=0, column=2, padx=5, sticky="w")
        
    def _on_set_clicked(self):
        # Ta metoda będzie wywoływana po kliknięciu przycisku SET
        # Implementacja zostanie dodana później
        pass
        
    def get_frame(self):
        return self.frame
        
    def get_initial_time(self):
        return self.initial_time_var.get()
        
    def set_initial_time(self, value):
        self.initial_time_var.set(value)
        
    def get_time_in_seconds(self):
        try:
            hours, minutes = map(int, self.initial_time_var.get().split(':'))
            return hours * 3600 + minutes * 60
        except ValueError:
            return 0 