from GUI import GUI
from output import OutputDF
from inputData import InputData
import Tkinter as tk
from Tkinter import *

def main():
    root = tk.Tk()
    root.title("Test")
    root.geometry('1024x960')

    gui = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
