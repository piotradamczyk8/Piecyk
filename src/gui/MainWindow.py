import tkinter as tk
from tkinter import ttk
from src.gui.frames.ControlsFrame import ControlsFrame
from src.gui.frames.PlotFrame import PlotFrame

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1440x1080")
        self.root.title("Kiln Control System")
        
        # Inicjalizacja ramek
        self.controls_frame = ControlsFrame(self.root)
        self.plot_frame = PlotFrame(self.root)
        
    def start(self):
        self.root.mainloop()
        
    def get_root(self):
        return self.root 