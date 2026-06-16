from tkinter import Tk, Button, _tkinter, Label, Frame, Canvas, Event, colorchooser, StringVar, OptionMenu, Listbox, Entry, Toplevel
#from tkinter.ttk import Widget, ComboBox
from _tkinter import TclError
import tkinter.ttk as ttk
class WindowBuilder:

    def __init__(self, window):
        self.init_root(window)
        self.init_root_geometry(window)
        self.build_window_title_bar(window)
        self.build_window_canvas(window)
        self.build_window_button_panel(window)
        window.root.update_idletasks()

    def init_root(self, window):
        window.root = Tk()
        window.root.geometry("1375x536")
        if (window.system == "Linux"):
            window.root.attributes("-type", "splash")
            #window.root.attributes("-type", "toolbar")

        #window.root.bind_all("<KeyPress>", window.key_pressed)
        window.root.bind_all("<Escape>", lambda event: window.terminate_entire_program(event))
        window.root.bind_all("<Control-z>", window.undo_previous_shape)
        
    def init_root_geometry(self, window):
        window.root.geometry("1375x536")
        window.root.columnconfigure(0, weight=1)
        window.root.columnconfigure(1, weight=1)
        window.root.rowconfigure(0, weight=1)
        window.root.rowconfigure(1, weight=1)

    def build_window_title_bar(self, window):
        window.title_bar = Frame(window.root, bg="gray20", height=30, relief="ridge", borderwidth=2)
        
        window.title_bar.grid(row=0, column=0, sticky="new", columnspan=3)
        window.title_bar.rowconfigure(0, weight=1)
        window.title_bar.columnconfigure(0, weight=1)
        window.title_bar.columnconfigure(1)
        window.title_bar.columnconfigure(2)
        window.title_bar.columnconfigure(3)

        window.title_bar_label = Label(window.title_bar, text="Map Maker", background="grey20", fg="white")
        window.title_bar_label.grid(row=0, column=0)
        window.title_bar_label.bind("<Motion>", window.move_window_around)
        window.title_bar_label.bind("<ButtonPress-1>", window.move_window_around)
        window.title_bar_label.bind("<ButtonRelease-1>", window.move_window_around)
        

        window.minimize = Button(window.title_bar, text="_", command=window.root.withdraw, width=1)
        window.minimize.grid(row=0, column=1, sticky="ne")
        window.maximize = Button(window.title_bar, text="O", command=window.zoom_out, width=1)
        window.maximize.grid(row=0, column=2, sticky="ne")
        window.title_quit = Button(window.title_bar, text="x", command=window.terminate_entire_program, width=1)
        window.title_quit.grid(row=0, column=3, sticky="ne")

    def build_window_canvas(self, window):
        window.canvas = Canvas(window.root, **{"width":1000, "height":500, "borderwidth":5, "relief":"ridge", "background":"grey90"},
                               takefocus=True)
        window.canvas.grid(row=1, column=1, sticky="nsew")

    def build_window_button_panel(self, window):
        window.button_panel = Frame(window.root, borderwidth=5, relief="ridge")
        window.button_panel.grid(row=1, column=0, sticky="new") # where it is relative inside self.root


        window.button_panel.columnconfigure(0, weight = 1, uniform="button_panel_col", minsize=100)
        window.button_panel.rowconfigure(0, uniform="button_panel_row")
        window.button_panel.rowconfigure(1, uniform="button_panel_row")
        window.button_panel.rowconfigure(2, uniform="button_panel_row")
        window.button_panel.rowconfigure(3, uniform="button_panel_row")
        window.button_panel.rowconfigure(4, weight = 1)

        window.export = Button(window.button_panel, text="EXPORT", command=window.export_shapes, width=1, height=1)
        window.import_ = Button(window.button_panel, text="IMPORT", command=window.import_shapes, width=1, height=1)
        window.color_picker1 = Button(window.button_panel, text="FILL", command=window.fill_color_picker, width=1, height=1)
        window.color_picker2 = Button(window.button_panel, text="OUTLINE", command=window.outline_color_picker, width=1, height=1)

        window.shape_selection = Listbox(window.button_panel,font=("Arial", 16, "bold"), justify="center", width=8, borderwidth=1, relief="ridge")
        window.shape_selection.bind("<<ListboxSelect>>", window.update_shape_type)
        window.shape_selection.insert("end", "rectangle")
        window.shape_selection.insert("end", "oval")
        window.shape_selection.insert("end", "circle")
        #window.shape_selection.insert("end", "highdef circle")

        window.export.grid(row=0, column=0, sticky="new")
        window.import_.grid(row=1, column=0, sticky="new")
        window.color_picker1.grid(row=2, column=0, sticky="new")
        window.color_picker2.grid(row=3, column=0, sticky="new")
        window.shape_selection.grid(row=4, column=0, sticky="new")
