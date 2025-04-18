import tkinter as tk
from tkinter import ttk

class TriacFrame:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=5)
        
        # Zmienne
        self.cycle_var = tk.StringVar(value="0")
        self.impulse_after_var = tk.StringVar(value="0")
        self.zero_crossing_var = tk.StringVar(value="0")
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Etykieta i pole tekstowe dla cyklu
        tk.Label(self.frame, text="Cycle (ms):").grid(row=0, column=0, padx=5, sticky="w")
        self.cycle_entry = tk.Entry(self.frame, textvariable=self.cycle_var, width=10, state='readonly')
        self.cycle_entry.grid(row=0, column=1, padx=5, sticky="w")
        
        # Etykieta i pole tekstowe dla czasu włączenia
        tk.Label(self.frame, text="Triac on (ms):").grid(row=1, column=0, padx=5, sticky="w")
        self.impulse_after_entry = tk.Entry(self.frame, textvariable=self.impulse_after_var, width=10, state='readonly')
        self.impulse_after_entry.grid(row=1, column=1, padx=5, sticky="w")
        
        # Etykieta i pole tekstowe dla przejścia przez zero
        tk.Label(self.frame, text="Zero crossing:").grid(row=2, column=0, padx=5, sticky="w")
        self.zero_crossing_entry = tk.Entry(self.frame, textvariable=self.zero_crossing_var, width=10, state='readonly')
        self.zero_crossing_entry.grid(row=2, column=1, padx=5, sticky="w")
        
        # Przycisk ZERO
        self.zero_button = tk.Button(self.frame, text="ZERO", command=self._on_zero_clicked)
        self.zero_button.grid(row=0, column=2, rowspan=3, padx=5, sticky="w")
        
    def _on_zero_clicked(self):
        # Ta metoda będzie wywoływana po kliknięciu przycisku ZERO
        # Implementacja zostanie dodana później
        pass
        
    def get_frame(self):
        return self.frame
        
    def get_cycle(self):
        return float(self.cycle_var.get())
        
    def get_impulse_after(self):
        return float(self.impulse_after_var.get())
        
    def get_zero_crossing(self):
        return float(self.zero_crossing_var.get())
        
    def set_cycle(self, value):
        self.cycle_var.set(str(value))
        
    def set_impulse_after(self, value):
        self.impulse_after_var.set(str(value))
        
    def set_zero_crossing(self, value):
        self.zero_crossing_var.set(str(value))
        
    def get_triac_data(self):
        return {
            'cycle': self.get_cycle(),
            'impulse_after': self.get_impulse_after(),
            'zero_crossing': self.get_zero_crossing()
        } 