import tkinter as tk
from tkinter import ttk

class TimeFrame:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=5)
        
        # Zmienne dla czasu
        self.elapsed_time_var = tk.StringVar(value="00:00:00")
        self.remaining_time_var = tk.StringVar(value="00:00:00")
        self.final_time_var = tk.StringVar(value="00:00:00")
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Etykieta i pole tekstowe dla upływającego czasu
        tk.Label(self.frame, text="Elapsed Time:").grid(row=0, column=0, padx=5, sticky="w")
        self.elapsed_time_entry = tk.Entry(self.frame, textvariable=self.elapsed_time_var, width=10, state='readonly')
        self.elapsed_time_entry.grid(row=0, column=1, padx=5, sticky="w")
        
        # Etykieta i pole tekstowe dla pozostałego czasu
        tk.Label(self.frame, text="Remaining Time:").grid(row=1, column=0, padx=5, sticky="w")
        self.remaining_time_entry = tk.Entry(self.frame, textvariable=self.remaining_time_var, width=10, state='readonly')
        self.remaining_time_entry.grid(row=1, column=1, padx=5, sticky="w")
        
        # Etykieta i pole tekstowe dla czasu końcowego
        tk.Label(self.frame, text="Final Time:").grid(row=2, column=0, padx=5, sticky="w")
        self.final_time_entry = tk.Entry(self.frame, textvariable=self.final_time_var, width=10, state='readonly')
        self.final_time_entry.grid(row=2, column=1, padx=5, sticky="w")
        
    def get_frame(self):
        return self.frame
        
    def get_elapsed_time(self):
        return self.elapsed_time_var.get()
        
    def get_remaining_time(self):
        return self.remaining_time_var.get()
        
    def get_final_time(self):
        return self.final_time_var.get()
        
    def set_elapsed_time(self, value):
        self.elapsed_time_var.set(value)
        
    def set_remaining_time(self, value):
        self.remaining_time_var.set(value)
        
    def set_final_time(self, value):
        self.final_time_var.set(value)
        
    def get_time_data(self):
        return {
            'elapsed': self.get_elapsed_time(),
            'remaining': self.get_remaining_time(),
            'final': self.get_final_time()
        } 