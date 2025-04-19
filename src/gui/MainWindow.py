import tkinter as tk
from tkinter import ttk

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1440x1080")
        self.root.title("Kiln Control System")
        
    def start(self):
        self.root.mainloop()
        
    def get_root(self):
        return self.root 