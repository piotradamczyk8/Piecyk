import tkinter as tk
from tkinter import ttk

class PowerControlFrame:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=5)
        
        # Zmienne
        self.power_var = tk.StringVar(value="0")
        self.cycle_var = tk.StringVar(value="0")
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Etykieta i pole tekstowe dla mocy
        tk.Label(self.frame, text="Power (%):").grid(row=0, column=0, padx=5, sticky="w")
        self.power_entry = tk.Entry(self.frame, textvariable=self.power_var, width=10)
        self.power_entry.grid(row=0, column=1, padx=5, sticky="w")
        
        # Etykieta i pole tekstowe dla cyklu
        tk.Label(self.frame, text="Cycle (ms):").grid(row=1, column=0, padx=5, sticky="w")
        self.cycle_entry = tk.Entry(self.frame, textvariable=self.cycle_var, width=10)
        self.cycle_entry.grid(row=1, column=1, padx=5, sticky="w")
        
        # Przycisk SET
        self.set_button = tk.Button(self.frame, text="SET", command=self._on_set_clicked)
        self.set_button.grid(row=0, column=2, rowspan=2, padx=5, sticky="w")
        
    def _on_set_clicked(self):
        # Ta metoda będzie wywoływana po kliknięciu przycisku SET
        # Implementacja zostanie dodana później
        pass
        
    def get_frame(self):
        return self.frame
        
    def get_power(self):
        return float(self.power_var.get())
        
    def get_cycle(self):
        return float(self.cycle_var.get())
        
    def set_power(self, value):
        self.power_var.set(str(value))
        
    def set_cycle(self, value):
        self.cycle_var.set(str(value)) 