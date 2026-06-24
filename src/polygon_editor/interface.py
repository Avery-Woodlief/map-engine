from vertex_drawer import *
from tkinter.colorchooser import Chooser
from tkinter.dialog import Dialog
from color_wheel import *

class SimpleButton(Button):
    def __init__(self, parent, text_, command_):
        super().__init__(parent, text=text_, command=command_)
        #self.id = kw["text"]
        self.id = text_
class Interface:

    def __init__(self, init_width, init_height):

        if (not (isinstance(init_width, int) and isinstance(init_height, int))):
            raise ValueError(f"both init interface width and init interface height are bad types, got type {type(init_width)} and {type(init_height)}")
        elif (not (init_width > 0 and init_height > 0)):
            raise ValueError(f"neither init interface width nor init interface height are positive integers")
        elif (not (init_width > 0)):
            raise ValueError("init interface width is not positive integer")
        elif (not (init_height > 0)):
            raise ValueError("init interface height is not positive integer")
        elif (not isinstance(init_width, int)):
            raise ValueError(f"bad init interface width type, got {type(init_width)}")
        elif (not isinstance(init_height, int)):
            raise ValueError(f"bad init interface height type, got {type(init_height)}")
        self.root = Tk()
        self.root.geometry(f"{init_width}x{init_height}")
        self.root.columnconfigure(0)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.update_idletasks()
        ColorWheel(self.root)
        self.graph = Graph(nint(init_width - 50), nint(init_height/2), self.root)
        self.graph.root.update_idletasks()

        Button(self.root, text="+", command=self.add_poly).grid(column=1, row=0, sticky="wns")#.place(x=self.graph.winfo_x()-50, y=self.graph.winfo_y())
        
        self.polygon_buttons = {i + 1 : "" for i in range(len(self.graph.polygons))}

        for i in range(len(self.graph.polygons)):
            polygon_number = i + 1
            self.polygon_buttons[polygon_number] = Button(self.root, text=f"{polygon_number}", command=lambda n=polygon_number: self.select_polygon(n),
                                                          width=2) 
            self.polygon_buttons[polygon_number].place(x=self.graph.winfo_x() + 50 + i*(50), y=self.graph.winfo_y() + self.graph.winfo_height())
            self.polygon_buttons[polygon_number].bind("<Enter>", lambda event, n=polygon_number: self.polygon_preview(event,n))

        #Chooser().pack(self.root)
        

        self.root.bind("<KeyPress-Tab>", self.switch_windows)

        self.root.mainloop()


    def polygon_preview(self, event, num):
        self.graph.selected_polygon = num-1
        self.graph.grid.redraw(event=None)


    def select_polygon(self, num):
        print(f"selecting {num}")
        self.graph.selected_polygon = num-1
        self.graph.grid.redraw(event=None)

    def add_poly(self):
        index = len(self.graph.polygons)
        slot_y = self.graph.winfo_y() + self.graph.winfo_height() + (len(list(self.polygon_buttons.keys()))//12)*(25)
        self.graph.polygons.append(Polygon(self.graph, "black", f"polygon - {index + 1}"))
        self.polygon_buttons[index + 1] = Button(self.root, text=f"{index + 1}", command=lambda n=(index + 1): self.select_polygon(n))
        self.polygon_buttons[index + 1].place(x=self.graph.winfo_x() + 50 + ((index) % 12)*(50), y=slot_y)
        self.polygon_buttons[index + 1].bind("<Enter>", lambda event, n=(index + 1): self.polygon_preview(event,n))
        
    def switch_windows(self, event):
        #print(self.graph.root.focus_get())
        #print(self.graph.path)
        if (self.graph.has_focus):
            self.root.focus_set()
            self.graph.has_focus = False
        else:
            widget = self.root.nametowidget(self.graph.path)
            widget.focus_set()
            self.graph.has_focus = True
            print(widget.focus_get())

ui = Interface(1000, 800)
