import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.classes.TemperaturePlot import TemperaturePlot

class PlotFrame:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # Inicjalizacja wykresu
        self.fig = Figure(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Inicjalizacja klasy TemperaturePlot
        self.temperature_plot = TemperaturePlot(self.frame)
        
    def get_frame(self):
        return self.frame
        
    def get_temperature_plot(self):
        return self.temperature_plot 