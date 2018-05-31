import Tkinter as tk
from Tkinter import *
import tkMessageBox as mb
import tkFileDialog
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg


from output import OutputDF
from inputData import InputData
from flag import FlagDF
import utils

import os.path
import os
import numpy as np

class GUI:

    def __init__(self, master):
        self.master = master
        self.input_data = None
        self.output_df = OutputDF()      # OutputDF()
        self.flag_df = FlagDF()         # or create a new data type

        self.pre_frame = tk.Frame(self.master, bg='gray')
        self.info_frame = tk.Frame(self.master)
        self.canvas = tk.Frame(self.master)
        self.tool_frame = tk.Frame(self.master)
        self.channel_frame = tk.Frame(self.master)
        self.selected_canvas = tk.Frame(self.master)
        self.selected_toolbar = tk.Frame(self.master)

        for r in range(19):
            self.master.rowconfigure(r, weight=1)    
        for c in range(10):
            self.master.columnconfigure(c, weight=1)
        self.pre_frame.grid(column=0, row=0, rowspan=5, sticky = W+E+N+S)
        self.info_frame.grid(column=0, row=5, rowspan=6, sticky = W+E+N+S)
        self.channel_frame.grid(column=0, row=11, rowspan=7,sticky = W+E+N+S)
        self.canvas.grid(column=1, row=0, rowspan=10, columnspan=9, sticky = W+E+N+S)
        self.tool_frame.grid(column=1, row=10, columnspan=9, sticky = W+E+N+S)
        self.selected_canvas.grid(column=1, row=11, columnspan=9, rowspan=7,sticky = W+E+N+S)
        self.selected_toolbar.grid(column=1, row=18,columnspan=9, sticky = W+E+N+S)
        self.pre_frame.grid_propagate(False)
        self.canvas.grid_propagate(False)
        self.tool_frame.grid_propagate(False)
	self.selected_canvas.grid_propagate(False)
	self.selected_width = self.selected_canvas.winfo_width()+5
	self.selected_height = self.selected_canvas.winfo_height()+5

        self.response = IntVar()
        self.response.set(0)

        self.choose_file_button = tk.Button(self.pre_frame, text="choose file", command=self.load_file)
        self.save_button = tk.Button(self.pre_frame, text='save', command=self.save)
        self.quit_button = tk.Button(self.pre_frame, text='quit', command=self.quit)
        self.choose_file_button.grid()
        self.save_button.grid()
        self.quit_button.grid()

        # create radio button for yes and no
        self.yes = Radiobutton(self.pre_frame, text='yes', variable=self.response, value=1, command=self.display)
        self.no = Radiobutton(self.pre_frame, text='no', variable=self.response, value=0, command=self.display)

        self.prevbutton = tk.Button(self.pre_frame, text='prev', command=self.prev)
        self.nxtbutton = tk.Button(self.pre_frame, text='next', command=self.nxt)

        self.listbox = tk.Listbox(self.channel_frame, selectmode=MULTIPLE, height=2)

        self.starting = False

    def load_file(self):
        self.master.filename = tkFileDialog.askopenfilename(initialdir = "~/Desktop/Research",
                                                title = "Select file",
                                                filetypes = (("edf files","*.edf"),("h5py files", "*.h5"),("all files","*.*")))
        self.input_data = utils.load_file(self.master.filename)
        print self.master.filename
        if self.input_data == None:
            mb.showerror("Error", "File not found!")
            return
        else:
            self.to_start_state()
            l = tk.Label(self.pre_frame, text="data loaded")
            l.grid()
        
        # prompt for flag file
        res = mb.askyesno("Search for flag file", "Do you want to search for flag file?")
        found_flag = False
        while res == 1:
            flag_name = tkFileDialog.askopenfilename(initialdir = "~/Desktop/Research",
                                                title = "Select file",
                                                filetypes = (("response files","*.response"),("all files","*.*")))
            self.flag_df.load_from_file(flag_name, self.master.filename)
            if self.flag_df.filename == None:
                res = mb.askyesno("Fail", "Load flag file failed. Try again?")
            else:
                found_flag = True

        # prompt for response file
        res = mb.askyesno("Search for response", "Do you want to search for previous response file?")
        while res == 1:
            response_name = tkFileDialog.askopenfilename(initialdir = "~/Desktop/Research",
                                                title = "Select file",
                                                filetypes = (("response files","*.response"),("all files","*.*")))
            self.output_df.load_response(response_name, self.master.filename, self.flag_df.filename)
            print self.output_df.responses
            if self.output_df.filename == None:
                res = mb.askyesno("Fail", "Load response file failed. Try again?")
            else:
                res = -1
        if res == 0:    # no response file, create one base on either default criterion or flag file
            if found_flag:
                self.output_df.create_on_flag(self.flag_df)
            else:
                self.output_df.create_on_input(self.input_data, self.master.filename)


        self.start()
    
    def to_start_state(self):
        print "start to_start_state"
        self.unpack_frame(self.pre_frame)
        self.clear_frame(self.canvas)
        self.clear_frame(self.tool_frame)
        self.clear_frame(self.info_frame)
        self.choose_file_button.grid()
        self.save_button.grid()
        self.quit_button.grid()
        print "end to_start_state"


    def start(self):
        self.starting = True
        self.yes.grid()
        self.no.grid()
        self.master.bind('<y>', self.display_event)
        self.master.bind('<n>', self.display_event)
        self.master.bind('<Left>', self.prevkey)
        self.master.bind('<Right>', self.nextkey)
        self.prevbutton.grid()
        self.nxtbutton.grid()
        self.display()
    
    def display_event(self, event):
        if event.char == 'y':
            self.response.set(1)
        else:
            self.response.set(0)
        self.display()
    
    def save(self):
        output_filename = tkFileDialog.asksaveasfilename(initialdir = "/",title = "Save file",filetypes = (("response files","*.response"),("all files","*.*")))
        output_dir = '/'.join(output_filename.split('/')[:-1])
        while not os.access(output_dir, os.W_OK):
            mb.showinfo('Warning', 'Not writable')
            output_filename = tkFileDialog.asksaveasfilename(initialdir = "/",title = "Save file",filetypes = (("response files","*.response"),("all files","*.*")))
            output_dir = '/'.join(output_filename.split('/')[:-1])

        if len(output_filename) < 9 or output_filename[-9:] != '.response':
            output_filename += '.response'
        self.output_df.filename = output_filename
        self.output_df.save()
        mb.showinfo("Response saved", "Successfully saved response!")

    def unpack_frame(self, frame):
        for wi in frame.winfo_children():
            wi.grid_forget()    
    
    def clear_frame(self, frame):
        for wi in frame.winfo_children():
            wi.destroy()

    def display(self):
        self.clear_frame(self.canvas)
        self.clear_frame(self.tool_frame)
        self.clear_frame(self.info_frame)
        self.clear_frame(self.channel_frame)
        self.clear_frame(self.selected_canvas)
        self.clear_frame(self.selected_toolbar)

	matplotlib.pyplot.close("all")
        done = self.output_df.update_one(self.response.get(), self.starting)
        self.starting = False
        if done:
            mb.showinfo("All done!", "Good job!")
            self.to_start_state()
            return
        fig = utils.draw_figure(self.input_data, self.output_df)
        canvas2 = FigureCanvasTkAgg(fig, master=self.canvas)
        c = canvas2.get_tk_widget()
        c.pack(side=tk.RIGHT, expand=True, fill=BOTH)
        toolbar = NavigationToolbar2TkAgg(canvas2, self.tool_frame)
        toolbar.update()

        self.display_bad_labels()
        self.add_listbox()
    
    def add_listbox(self):
        self.listbox = tk.Listbox(self.channel_frame, selectmode=MULTIPLE)
        for i in xrange(self.input_data.num_channels):
            self.listbox.insert(END, str(i))
        self.listbox.grid()
        confirm_button = tk.Button(self.channel_frame, text='draw figure', command=self.draw_selected_channels)
        confirm_button.grid()
    
    def draw_selected_channels(self):
	self.clear_frame(self.selected_canvas)
        self.clear_frame(self.selected_toolbar)
	matplotlib.pyplot.close("all")
        selected = [int(self.listbox.get(i)) for i in self.listbox.curselection()]
        fig = utils.draw_selected(selected, self.input_data, self.output_df)
        canvas2 = FigureCanvasTkAgg(fig, master=self.selected_canvas)
        c = canvas2.get_tk_widget()
        c.pack(side=tk.RIGHT, expand=True, fill=BOTH)
        c.configure(width=self.selected_width, height=self.selected_height)
        toolbar = NavigationToolbar2TkAgg(canvas2, self.selected_toolbar)
        toolbar.update()

    
    def display_bad_labels(self):
        l = tk.Label(self.info_frame, text="bad labels:")
        l.grid()
        bad_channels = np.where(self.output_df.channels[self.output_df.now_displaying])[0]
        for chan in bad_channels:
            st = str(chan)
            if (self.input_data.labels != None):
                st = st + ': ' + self.input_data.labels[chan]
            label = tk.Label(self.info_frame, text=st)
            label.grid()

    def nextkey(self, event):
        self.nxt()

    def prevkey(self, event):
        self.prev()

    def prev(self):
        self.starting = True
        self.output_df.now_displaying -= 2
        if (self.output_df.now_displaying < -1):
            mb.showerror("Error", "This is the first one!")
            return
        self.display()
    
    def nxt(self):
        self.response.set(self.output_df.responses[self.output_df.now_displaying])
        self.display()
    
    def quit(self):
        res = mb.askyesno("Quit", "Are you sure to quit?")
        if res:
            res = mb.askyesno("Save", "Save current response?")
            if res:
                self.save()
            self.master.quit()

