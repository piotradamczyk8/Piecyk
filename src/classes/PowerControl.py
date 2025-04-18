import tkinter as tk
from tkinter import ttk

class PowerControl:
    def __init__(self, parent_frame):
        self.frame = ttk.LabelFrame(parent_frame, text="Sterowanie Mocą")
        self.frame.pack(fill=tk.X, padx=5, pady=5)

        # Zmienne
        self.power_var = tk.StringVar(value="0")
        self.power_scale_var = tk.DoubleVar(value=0)
        self.power_scale_var.trace_add('write', self.on_power_change)

        # Etykiety
        ttk.Label(self.frame, text="Moc:").grid(row=0, column=0, padx=5, pady=5)
        self.power_label = ttk.Label(self.frame, textvariable=self.power_var)
        self.power_label.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.frame, text="%").grid(row=0, column=2, padx=5, pady=5)

        # Suwak
        self.power_scale = ttk.Scale(self.frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                   variable=self.power_scale_var, command=self.on_scale_move)
        self.power_scale.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)

    def on_power_change(self, *args):
        """Aktualizuje wartość mocy przy zmianie suwaka."""
        power = self.power_scale_var.get()
        self.power_var.set(f"{power:.1f}")

    def on_scale_move(self, value):
        """Obsługuje ruch suwaka."""
        power = float(value)
        self.power_var.set(f"{power:.1f}")

    def get_power(self):
        """Zwraca aktualną wartość mocy."""
        return self.power_scale_var.get()

    def set_power(self, value):
        """Ustawia wartość mocy."""
        self.power_scale_var.set(value) 