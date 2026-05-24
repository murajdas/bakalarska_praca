import sys
from gui import WordNetworkGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = WordNetworkGUI(root)
    root.mainloop()