import tkinter as tk
from tkinter import ttk
from src.classes.TemperatureCurves import TemperatureCurves

class TemperatureCurveFrame:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=5)
        
        # Zmienne
        self.curve_var = tk.StringVar()
        self.curves = TemperatureCurves()
        
        # Ustawienie wartości początkowej
        curve_names = self.curves.get_curve_names()
        if curve_names:
            self.curve_var.set(curve_names[0])
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Etykieta i menu wyboru krzywej
        tk.Label(self.frame, text="Temperature Curve:").grid(row=0, column=0, padx=5, sticky="w")
        
        # Utworzenie menu z wartością początkową i opcjami
        self.curve_menu = tk.OptionMenu(self.frame, self.curve_var, self.curve_var.get(), *self.curves.get_curve_names())
        self.curve_menu.grid(row=0, column=1, padx=5, sticky="w")
        
        # Przycisk SET
        self.set_button = tk.Button(self.frame, text="SET", command=self._on_set_clicked)
        self.set_button.grid(row=0, column=2, padx=5, sticky="w")
        
    def _on_set_clicked(self):
        # Ta metoda będzie wywoływana po kliknięciu przycisku SET
        # Implementacja zostanie dodana później
        pass
        
    def get_frame(self):
        return self.frame
        
    def get_selected_curve(self):
        return self.curve_var.get()
        
    def set_selected_curve(self, curve_name):
        self.curve_var.set(curve_name)
        
    def get_curve_data(self):
        return self.curves.get_curve_data(self.get_selected_curve())
        
    def get_curve_names(self):
        return self.curves.get_curve_names() 