from GUI import GUI
from output import OutputDF
from inputData import InputData
import tkinter as tk
from tkinter import *

def main():
    root = tk.Tk()
    root.title("Test")
    root.geometry('1024x960')   # change the size of window here

    gui = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
