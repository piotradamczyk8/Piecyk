import tkinter as tk
from tkinter import ttk

class TemperatureFrame:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=5)
        
        # Zmienne dla temperatury
        self.thermocouple_var = tk.StringVar(value="0")
        self.approximate_var = tk.StringVar(value="0")
        self.expected_var = tk.StringVar(value="0")
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Etykieta i pole tekstowe dla temperatury z termopary
        tk.Label(self.frame, text="Thermocouple (°C):").grid(row=0, column=0, padx=5, sticky="w")
        self.thermocouple_entry = tk.Entry(self.frame, textvariable=self.thermocouple_var, width=10, state='readonly')
        self.thermocouple_entry.grid(row=0, column=1, padx=5, sticky="w")
        
        # Etykieta i pole tekstowe dla temperatury przybliżonej
        tk.Label(self.frame, text="Approximate (°C):").grid(row=1, column=0, padx=5, sticky="w")
        self.approximate_entry = tk.Entry(self.frame, textvariable=self.approximate_var, width=10, state='readonly')
        self.approximate_entry.grid(row=1, column=1, padx=5, sticky="w")
        
        # Etykieta i pole tekstowe dla temperatury oczekiwanej
        tk.Label(self.frame, text="Expected (°C):").grid(row=2, column=0, padx=5, sticky="w")
        self.expected_entry = tk.Entry(self.frame, textvariable=self.expected_var, width=10, state='readonly')
        self.expected_entry.grid(row=2, column=1, padx=5, sticky="w")
        
    def get_frame(self):
        return self.frame
        
    def get_thermocouple_temp(self):
        return float(self.thermocouple_var.get())
        
    def get_approximate_temp(self):
        return float(self.approximate_var.get())
        
    def get_expected_temp(self):
        return float(self.expected_var.get())
        
    def set_thermocouple_temp(self, value):
        self.thermocouple_var.set(str(value))
        
    def set_approximate_temp(self, value):
        self.approximate_var.set(str(value))
        
    def set_expected_temp(self, value):
        self.expected_var.set(str(value))
        
    def get_temperature_data(self):
        return {
            'thermocouple': self.get_thermocouple_temp(),
            'approximate': self.get_approximate_temp(),
            'expected': self.get_expected_temp()
        } 