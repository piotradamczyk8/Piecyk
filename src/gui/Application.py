import tkinter as tk
from tkinter import ttk
from src.gui.MainWindow import MainWindow
from src.gui.frames.ControlsFrame import ControlsFrame
from src.gui.frames.InfoFrame import InfoFrame
from src.gui.frames.PlotFrame import PlotFrame
from src.gui.frames.IRFrame import IRFrame
from src.gui.frames.InitialTimeFrame import InitialTimeFrame
from src.gui.frames.PowerControlFrame import PowerControlFrame
from src.gui.frames.PIDControlFrame import PIDControlFrame
from src.gui.frames.ThermocoupleFrame import ThermocoupleFrame
from src.gui.frames.PZEMFrame import PZEMFrame
from src.gui.frames.TriacFrame import TriacFrame
from src.gui.frames.TemperatureCurveFrame import TemperatureCurveFrame
from src.gui.frames.TimeFrame import TimeFrame
from src.gui.frames.TemperatureFrame import TemperatureFrame
from src.gui.frames.PowerEnergyFrame import PowerEnergyFrame
from src.gui.frames.CycleTriacFrame import CycleTriacFrame

class Application:
    def __init__(self):
        # Inicjalizacja głównego okna
        self.main_window = MainWindow()
        self.root = self.main_window.get_root()
        
        # Inicjalizacja ramek
        self.controls_frame = ControlsFrame(self.root)
        #self.info_frame = InfoFrame(self.root)
        self.plot_frame = PlotFrame(self.root)
        self.ir_frame = IRFrame(self.root)
        self.initial_time_frame = InitialTimeFrame(self.root)
        self.power_control_frame = PowerControlFrame(self.root)
        self.pid_control_frame = PIDControlFrame(self.root)
        self.thermocouple_frame = ThermocoupleFrame(self.root)
        self.pzem_frame = PZEMFrame(self.root)
        self.triac_frame = TriacFrame(self.root)
        self.temperature_curve_frame = TemperatureCurveFrame(self.root)
        self.time_frame = TimeFrame(self.root)
        self.temperature_frame = TemperatureFrame(self.root)
        self.power_energy_frame = PowerEnergyFrame(self.root)
        self.cycle_triac_frame = CycleTriacFrame(self.root)
        
        # Konfiguracja układu ramek
        self._setup_layout()
        
    def _setup_layout(self):
        # Lewa strona - wykres
        self.plot_frame.get_frame().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Prawa strona - kontrolki
        right_frame = tk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Kontrolki w prawej ramce
        self.controls_frame.get_frame().pack(fill=tk.X, pady=5)
        #self.info_frame.get_frame().pack(fill=tk.X, pady=5)
        self.ir_frame.get_frame().pack(fill=tk.X, pady=5)
        self.initial_time_frame.get_frame().pack(fill=tk.X, pady=5)
        self.power_control_frame.get_frame().pack(fill=tk.X, pady=5)
        self.pid_control_frame.get_frame().pack(fill=tk.X, pady=5)
        self.thermocouple_frame.get_frame().pack(fill=tk.X, pady=5)
        self.pzem_frame.get_frame().pack(fill=tk.X, pady=5)
        self.triac_frame.get_frame().pack(fill=tk.X, pady=5)
        self.temperature_curve_frame.get_frame().pack(fill=tk.X, pady=5)
        self.time_frame.get_frame().pack(fill=tk.X, pady=5)
        self.temperature_frame.get_frame().pack(fill=tk.X, pady=5)
        self.power_energy_frame.get_frame().pack(fill=tk.X, pady=5)
        self.cycle_triac_frame.get_frame().pack(fill=tk.X, pady=5)
        
    def run(self):
        self.root.mainloop()
        
    def get_root(self):
        return self.root
        
    def get_plot_frame(self):
        return self.plot_frame
        
    def get_controls_frame(self):
        return self.controls_frame
        
    def get_info_frame(self):
        return self.info_frame
        
    def get_ir_frame(self):
        return self.ir_frame
        
    def get_initial_time_frame(self):
        return self.initial_time_frame
        
    def get_power_control_frame(self):
        return self.power_control_frame
        
    def get_pid_control_frame(self):
        return self.pid_control_frame
        
    def get_thermocouple_frame(self):
        return self.thermocouple_frame
        
    def get_pzem_frame(self):
        return self.pzem_frame
        
    def get_triac_frame(self):
        return self.triac_frame
        
    def get_temperature_curve_frame(self):
        return self.temperature_curve_frame
        
    def get_time_frame(self):
        return self.time_frame
        
    def get_temperature_frame(self):
        return self.temperature_frame
        
    def get_power_energy_frame(self):
        return self.power_energy_frame
        
    def get_cycle_triac_frame(self):
        return self.cycle_triac_frame 