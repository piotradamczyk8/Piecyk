import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

class InfoFrame:
    def __init__(self, parent: tk.Frame):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self._create_widgets()

    def _create_widgets(self):
        # Etykiety i pola tekstowe
        self.labels: Dict[str, ttk.Label] = {}
        self.entries: Dict[str, ttk.Entry] = {}
        
        # Dodanie pola dla aktualnego etapu
        self.labels["Current Stage"] = ttk.Label(self.frame, text="Current Stage:")
        self.entries["Current Stage"] = ttk.Entry(self.frame, state="readonly", width=20)
        
        # Pozostałe pola
        fields = ["Time", "Temperature", "Power", "Energy", "Cycles"]
        for field in fields:
            self.labels[field] = ttk.Label(self.frame, text=f"{field}:")
            self.entries[field] = ttk.Entry(self.frame, state="readonly", width=20)

        # Układanie widgetów
        for i, field in enumerate(["Current Stage"] + fields):
            self.labels[field].grid(row=i, column=0, padx=5, pady=2, sticky="e")
            self.entries[field].grid(row=i, column=1, padx=5, pady=2, sticky="w")

    def get_frame(self) -> tk.Frame:
        return self.frame

    def update_data(self, data: Dict[str, Any]) -> None:
        """Aktualizuje dane w polach tekstowych."""
        for key, value in data.items():
            if key in self.entries:
                self.entries[key].config(state="normal")
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, str(value))
                self.entries[key].config(state="readonly") 