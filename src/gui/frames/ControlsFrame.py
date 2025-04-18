import tkinter as tk
from tkinter import ttk
from src.gui.frames.InfoFrame import InfoFrame
from src.gui.frames.InitialTimeFrame import InitialTimeFrame
from src.gui.frames.IRFrame import IRFrame

class ControlsFrame:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=(10, 0), fill=tk.X)
        
        # Inicjalizacja podramek
        self.curve_frame = self._create_curve_frame()
        self.initial_time_frame = InitialTimeFrame(self.frame)
        self.progress_frame = self._create_progress_frame()
        self.info_frame = InfoFrame(self.frame)
        self.ir_frame = IRFrame(self.frame)
        self.finish_button = self._create_finish_button()
        
    def _create_curve_frame(self):
        frame = tk.Frame(self.frame)
        frame.pack(pady=(10, 10))
        
        curve_var = tk.StringVar(value="Bisquit")
        curve_option_menu = tk.OptionMenu(frame, curve_var, "Bisquit", "Bisquit_express", "Glazing", "Glazing_perfect", "Glazing_express")
        curve_option_menu.config(width=15)
        curve_option_menu.pack()
        
        return frame
        
    def _create_progress_frame(self):
        frame = tk.Frame(self.frame)
        frame.pack(pady=(0, 5))
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100, length=500, style="blue.Horizontal.TProgressbar")
        progress_bar.pack()
        
        style = ttk.Style()
        style.configure("blue.Horizontal.TProgressbar", troughcolor='white', background='navy', thickness=25)
        
        progress_label = tk.Label(frame, textvariable=progress_var, anchor="center", fg="white", bg="navy")
        progress_label.place(in_=progress_bar, relx=0.5, rely=0.5, anchor="center")
        
        return frame
        
    def _create_finish_button(self):
        button = tk.Button(self.frame, text="FINISH")
        button.pack(pady=(10, 10))
        return button
        
    def get_frame(self):
        return self.frame 