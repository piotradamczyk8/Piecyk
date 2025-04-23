import tkinter as tk

class LEDIndicator:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg='white')
        self.canvas = tk.Canvas(self.frame, width=20, height=20, bg='white', highlightthickness=0)
        self.canvas.pack()
        self.led = self.canvas.create_oval(2, 2, 18, 18, fill='white')
        self.is_on = False

    def turn_on(self):
        if not self.is_on:
            self.canvas.itemconfig(self.led, fill='red')
            self.is_on = True

    def turn_off(self):
        if self.is_on:
            self.canvas.itemconfig(self.led, fill='white')
            self.is_on = False

    def place(self, **kwargs):
        self.frame.place(**kwargs)

    def configure(self, **kwargs):
        self.frame.configure(**kwargs) 