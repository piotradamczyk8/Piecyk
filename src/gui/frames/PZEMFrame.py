import tkinter as tk
from tkinter import ttk

class PZEMFrame:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=5)
        
        # Zmienne dla odczytów PZEM
        self.voltage_var = tk.StringVar(value="0")
        self.current_var = tk.StringVar(value="0")
        self.power_var = tk.StringVar(value="0")
        self.energy_var = tk.StringVar(value="0")
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Etykieta i pole tekstowe dla napięcia
        tk.Label(self.frame, text="Voltage (V):").grid(row=0, column=0, padx=5, sticky="w")
        self.voltage_entry = tk.Entry(self.frame, textvariable=self.voltage_var, width=10, state='readonly')
        self.voltage_entry.grid(row=0, column=1, padx=5, sticky="w")
        
        # Etykieta i pole tekstowe dla prądu
        tk.Label(self.frame, text="Current (A):").grid(row=1, column=0, padx=5, sticky="w")
        self.current_entry = tk.Entry(self.frame, textvariable=self.current_var, width=10, state='readonly')
        self.current_entry.grid(row=1, column=1, padx=5, sticky="w")
        
        # Etykieta i pole tekstowe dla mocy
        tk.Label(self.frame, text="Power (W):").grid(row=2, column=0, padx=5, sticky="w")
        self.power_entry = tk.Entry(self.frame, textvariable=self.power_var, width=10, state='readonly')
        self.power_entry.grid(row=2, column=1, padx=5, sticky="w")
        
        # Etykieta i pole tekstowe dla energii
        tk.Label(self.frame, text="Energy (Wh):").grid(row=3, column=0, padx=5, sticky="w")
        self.energy_entry = tk.Entry(self.frame, textvariable=self.energy_var, width=10, state='readonly')
        self.energy_entry.grid(row=3, column=1, padx=5, sticky="w")
        
    def get_frame(self):
        return self.frame
        
    def get_voltage(self):
        return float(self.voltage_var.get())
        
    def get_current(self):
        return float(self.current_var.get())
        
    def get_power(self):
        return float(self.power_var.get())
        
    def get_energy(self):
        return float(self.energy_var.get())
        
    def set_voltage(self, value):
        self.voltage_var.set(str(value))
        
    def set_current(self, value):
        self.current_var.set(str(value))
        
    def set_power(self, value):
        self.power_var.set(str(value))
        
    def set_energy(self, value):
        self.energy_var.set(str(value))
        
    def get_pzem_data(self):
        return {
            'voltage': self.get_voltage(),
            'current': self.get_current(),
            'power': self.get_power(),
            'energy': self.get_energy()
        } 