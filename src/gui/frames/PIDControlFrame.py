import tkinter as tk
from tkinter import ttk

class PIDControlFrame:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=5)
        
        # Zmienne dla parametrów PID
        self.kp_var = tk.StringVar(value="0")
        self.ki_var = tk.StringVar(value="0")
        self.kd_var = tk.StringVar(value="0")
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Etykieta i pole tekstowe dla Kp
        tk.Label(self.frame, text="Kp:").grid(row=0, column=0, padx=5, sticky="w")
        self.kp_entry = tk.Entry(self.frame, textvariable=self.kp_var, width=10)
        self.kp_entry.grid(row=0, column=1, padx=5, sticky="w")
        
        # Etykieta i pole tekstowe dla Ki
        tk.Label(self.frame, text="Ki:").grid(row=1, column=0, padx=5, sticky="w")
        self.ki_entry = tk.Entry(self.frame, textvariable=self.ki_var, width=10)
        self.ki_entry.grid(row=1, column=1, padx=5, sticky="w")
        
        # Etykieta i pole tekstowe dla Kd
        tk.Label(self.frame, text="Kd:").grid(row=2, column=0, padx=5, sticky="w")
        self.kd_entry = tk.Entry(self.frame, textvariable=self.kd_var, width=10)
        self.kd_entry.grid(row=2, column=1, padx=5, sticky="w")
        
        # Przycisk SET
        self.set_button = tk.Button(self.frame, text="SET", command=self._on_set_clicked)
        self.set_button.grid(row=0, column=2, rowspan=3, padx=5, sticky="w")
        
    def _on_set_clicked(self):
        # Ta metoda będzie wywoływana po kliknięciu przycisku SET
        # Implementacja zostanie dodana później
        pass
        
    def get_frame(self):
        return self.frame
        
    def get_kp(self):
        return float(self.kp_var.get())
        
    def get_ki(self):
        return float(self.ki_var.get())
        
    def get_kd(self):
        return float(self.kd_var.get())
        
    def set_kp(self, value):
        self.kp_var.set(str(value))
        
    def set_ki(self, value):
        self.ki_var.set(str(value))
        
    def set_kd(self, value):
        self.kd_var.set(str(value))
        
    def get_pid_params(self):
        return {
            'kp': self.get_kp(),
            'ki': self.get_ki(),
            'kd': self.get_kd()
        } 