import re
from tkinter.colorchooser import Chooser
from tkinter.dialog import Dialog
from color_wheel import *
from vertex_drawer import *


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
        #self.root["bg"]="black"
        self.root.title("Polygon Editor")
        self.root.columnconfigure(0)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.update_idletasks()
        self.color_wheel = ColorWheel(self.root)
        self.graph = Graph(nint(init_width - 50), nint(init_height/2), self.root)
        self.graph.root.update_idletasks()

        self.draw_add_button()
        self.draw_polygon_buttons()
        

        self.root.bind("<KeyPress-Tab>", self.switch_windows)
        self.root.bind("~", self.check_for_refresh, add="+") #XXX restarts polygon editor
        self.root.bind("<Escape>", lambda e: self.root.quit())

        self.children = self.root.winfo_children()
        self.enabled_children = [child for child in self.children if not bool(re.search(r"button", str(child)))]
        self.disabled_children = [child for child in self.children if bool(re.search(r"button", str(child)))]
        self.current_child = self.enabled_children[0]
        self.current_child.focus_force()

        #print(self.enabled_children)
        #print(self.disabled_children)

        self.root.mainloop()

    def check_for_refresh(self,event=None):
        for k in self.polygon_buttons.keys():
            self.polygon_buttons[k].destroy()
        self.draw_polygon_buttons()
        self.root.update()
        

    def draw_add_button(self):
        Button(self.root, text="+", command=self.add_poly, takefocus=0).grid(column=1, row=0, sticky="wns")

    def draw_polygon_buttons(self):

        self.polygon_buttons = {i + 1 : "" for i in range(len(self.graph.polygons))}

        for i in range(len(self.graph.polygons)):
            polygon_number = i + 1
            self.polygon_buttons[polygon_number] = Button(self.root, 
                                                          text=f"{polygon_number}", 
                                                          command=lambda n=polygon_number: self.select_polygon(n), 
                                                          width=2,
                                                          takefocus=0) 
            self.polygon_buttons[polygon_number].place(x=self.graph.winfo_x() + 50 + i*(50), y=self.graph.winfo_y() + self.graph.winfo_height())
            self.polygon_buttons[polygon_number].bind("<Enter>", lambda event, n=polygon_number: self.polygon_preview(event,n))


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
        self.current_child = self.enabled_children[(self.enabled_children.index(self.current_child) + 1) % len(self.enabled_children)]
        print(self.current_child)
        if (str(self.current_child) in (".pallete_frame", ".mixture_frame")):
            print(self.current_child.winfo_children())
            self.color_wheel.selected_frame = self.current_child
            self.color_wheel.selected_canvas = self.current_child.winfo_children()[0]

        return

ui = Interface(1000, 800)
