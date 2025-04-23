import tkinter as tk

class LEDIndicator(tk.Label):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="red", width=2, height=1)
        self.turn_off()

    def turn_on(self):
        """Włącza wskaźnik LED."""
        self.configure(bg="red")

    def turn_off(self):
        """Wyłącza wskaźnik LED."""
        self.configure(bg="white") 