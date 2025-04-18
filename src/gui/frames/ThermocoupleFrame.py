import tkinter as tk
from tkinter import ttk

class ThermocoupleFrame:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=5)
        
        # Zmienne
        self.temperature_var = tk.StringVar(value="0")
        self.offset_var = tk.StringVar(value="0")
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Etykieta i pole tekstowe dla temperatury
        tk.Label(self.frame, text="Temperature (°C):").grid(row=0, column=0, padx=5, sticky="w")
        self.temperature_entry = tk.Entry(self.frame, textvariable=self.temperature_var, width=10, state='readonly')
        self.temperature_entry.grid(row=0, column=1, padx=5, sticky="w")
        
        # Etykieta i pole tekstowe dla offsetu
        tk.Label(self.frame, text="Offset (°C):").grid(row=1, column=0, padx=5, sticky="w")
        self.offset_entry = tk.Entry(self.frame, textvariable=self.offset_var, width=10)
        self.offset_entry.grid(row=1, column=1, padx=5, sticky="w")
        
        # Przycisk SET dla offsetu
        self.set_button = tk.Button(self.frame, text="SET", command=self._on_set_clicked)
        self.set_button.grid(row=1, column=2, padx=5, sticky="w")
        
    def _on_set_clicked(self):
        # Ta metoda będzie wywoływana po kliknięciu przycisku SET
        # Implementacja zostanie dodana później
        pass
        
    def get_frame(self):
        return self.frame
        
    def get_temperature(self):
        return float(self.temperature_var.get())
        
    def get_offset(self):
        return float(self.offset_var.get())
        
    def set_temperature(self, value):
        self.temperature_var.set(str(value))
        
    def set_offset(self, value):
        self.offset_var.set(str(value)) 