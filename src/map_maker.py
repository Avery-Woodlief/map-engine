from tkinter import Tk, Button, _tkinter, Label, Frame, Canvas, Event, colorchooser, StringVar, OptionMenu, Listbox, Entry, Toplevel
#from tkinter.ttk import Widget, ComboBox
from _tkinter import TclError
import tkinter.ttk as ttk
import re
import platform
import math
import json
import os


# valid relief arguments: flat, groove, raised, ridge, solid, sunken

# hex masks for event states


state_masks = {
                "button1":0x100,
                "button2":0x200,
                "button3":0x400,
                "motion":0x0
              }

nint = lambda x: (math.floor(x + 0.5) + math.ceil((2*x - 1)/4) - math.floor((2*x - 1)/4) - 1) # nearest integer function


class Shape:
    def __init__(self, topleft=None, width=None, height=None, center=None, radius=None, filled=None, end=None, color=None, outline=None):
        if (not topleft and not center):
            raise ValueError("not speficied shape")
        if ((topleft and width and height) or (topleft and end)):
            self.type = "rectangle"
            if (width and height and not end):
                self.width = self.w = width
                self.height = self.h = height
                self.end = (topleft[0] + self.width, topleft[1] + self.height)
            elif ((not (width and height)) and end):
                self.width = self.w = end[0]-topleft[0]
                self.height = self.h = end[1]-topleft[1]
            self.topleft = topleft
            self.x = self.topleft[0]
            self.y = self.topleft[1]
        if ((center and radius) or (center and end)):
            
            if (radius):
                cx, cy = center
                left   = cx - radius
                top    = cy - radius
                self.radius = radius
                if (not end):
                    self.end = (center[0] + self.radius, center[1] + self.radius)
                    self.width = self.end[0]-left
                    self.height = self.end[1]-top
            else:
                self.radius = nint(math.dist(center, end))
                cx, cy = center
                left   = cx - radius
                top    = cy - radius
                self.end = end
                self.width = self.end[0]-left
                self.height = self.end[1]-top
                if (self.width == self.height):
                    self.is_circle = True
                    self.type = "circle"
                else:
                    self.is_circle = False
                    self.type = "oval"
            self.center = center
        self.filled = filled
        self.color = color
        self.outline = outline
        self.export_color = "(229, 229, 229, 255)"
        self.export_outline = "(127, 127, 127, 255)"
    def __str__(self):
        pass
        
        

class Rect(Shape):
    def __init__(self, **kw):
        super().__init__(**kw)
    def __str__(self):
        return f"{self.x}, {self.y}, {self.w}, {self.h} : {self.color}"

    def get_dims(self):
        return f"{self.x}, {self.y}, {self.w}, {self.h}"
    def get_color(self):
        return f"{self.color}"

class Oval(Shape):
    def __init__(self, **kw):
        super().__init__(**kw)
    def __str__(self):
        if (self.is_circle):
            return f"{self.center[0]}, {self.center[1]}, {self.radius} : {self.color}"
        else:
            return f"{self.center[0]-self.width}, {self.center[1]-self.height}, {self.end[0]}, {self.end[1]}"

    def get_dims(self):
        if (not self.is_circle):
            return f"{self.center[0]-self.width}, {self.center[1]-self.height}, {self.end[0]}, {self.end[1]}"
        else:
            return f"{self.center[0]}, {self.center[1]}, {self.radius}"
    def get_color(self):
        return f"{self.color}"

class HighDefOval:
    def __init__(self, center = None, end = None, radius = None, filled = None, color = None, outline = None, w = 20, h = 20):
        if (not center and not end):
            raise ValueError("no center and no end for HighDefOval class")        
        self.center = center
        self.radius = nint(math.dist(center, end))
        self.color = color
        self.filled = filled
        self.outline = outline
        self.rects = []
        self.type = "high-def oval"
        self.w = w
        self.h = h
        try:
            self.draw_circle_using_rects()
        except(ZeroDivisionError):
            pass

    def draw_circle_using_rects(self):
        cx, cy = self.center

        w = self.w
        h = self.h
        radius = self.radius
        increment = math.floor((360)/(2*math.pi*radius/w))
        

        for d in range(0, 360, increment):
            angle = math.radians(d)

            x = nint(cx + radius * math.cos(angle))
            y = nint(cy + radius * math.sin(angle))

            args = {"topleft":(x, y),"width":w, "height":h, "color":self.color, "filled":self.filled, "outline":self.outline}

            new_rect = Rect(**args)
            self.rects.append(new_rect)

    def __str__(self):
        if (len(self.rects) == 0):
            return ""
        string = f"{self.rects[0]}"
        for i in range(1, len(self.rects)):
            string += f"\n{self.rects[i]}"
        return string

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

        window.root.bind_all("<KeyPress>", window.key_pressed)
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
        window.shape_selection.insert("end", "high-def oval")

        window.export.grid(row=0, column=0, sticky="new")
        window.import_.grid(row=1, column=0, sticky="new")
        window.color_picker1.grid(row=2, column=0, sticky="new")
        window.color_picker2.grid(row=3, column=0, sticky="new")
        window.shape_selection.grid(row=4, column=0, sticky="new")

class DrawingBoard:
    def __init__(self):
        self.shape_args = {
                "rectangle": {
                                "topleft":None,
                                "width":None,
                                "end":None,
                                "height":None
                              },
                "oval": {
                            "center":None,
                            "end":None,
                            "radius":0
                          },
                "circle": {
                            "center":None,
                            "end":None,
                            "radius":0
                          },
                "high-def oval": {
                                    "center":None,
                                    "end":None,
                                    "radius":0
                                 },
                "style": {
                            "filled":None,
                            "color":"grey90",
                            "outline":"grey50"
                         },

                "export": {
                            "color":"(229, 229, 229, 255)",
                            "outline":"(127, 127, 127, 255)"
                          }
                
             }
        self.shape_counter = {"rectangle":0, "oval":0, "circle":0, "high-def oval":0}
        self.current_shape_type = "oval"#"rectangle"
        self.shapes = []
        self.system = platform.system()
        if (self.system == "Windows"):
            self.file_nav_char = "\\"
        else:
            self.file_nav_char = "/"
        self.zoom_bool = False
        self.window_event_x = 0
        self.window_event_y = 0
        self.bad_file_name_label_text = ""
        self.export_failed = False

        WindowBuilder(self)
        
        self.bind_commands(self.canvas, {"<Motion>":self.start_dragging_button1,
                                         "<ButtonPress-1>":self.start_dragging_button1,
                                         "<ButtonRelease-1>":self.end_dragging_button1,
                                         "<Button-4>":self.radius_adjuster,
                                         "<Button-5>":self.radius_adjuster,
                                         "<MouseWheel>":self.radius_adjuster})

        #self.canvas.bind("<Button-1>",lambda event: self.canvas.focus_set(),add="+")
        #self.root.bind_all("<ButtonPress>",lambda event: self.force_keyboard_focus(),add="+")
        self.title_bar.bind("<Motion>", self.move_window_around)
        self.title_bar.bind("<ButtonPress-1>", self.move_window_around)
        self.title_bar.bind("<ButtonRelease-1>", self.move_window_around)
        #self.root.bind_all("<Control-z>",self.undo_previous_shape)

        self.run()

    def terminate_entire_program(self, event=None):
        self.root.attributes("-topmost", False)
        self.root.update_idletasks()
        self.root.update()
        self.root.quit()
        return

    def ask_name(self):

        self.root.attributes("-topmost", False)
        self.file_name = ""

        popup = Toplevel(self.root)
        popup.attributes("-topmost", True)
        popup.title("Map Maker - Export")
        try:
            if (len(self.bad_file_name_label_text) > 0):
                warning = Label(popup, text=self.bad_file_name_label_text, fg="darkred")
                warning.pack()
                upper_bound_width = warning.winfo_reqwidth()
                upper_bound_height = warning.winfo_reqheight()
                popup.geometry(f"{upper_bound_width}x{150 + upper_bound_height}")
                label = Label(popup, text="Enter a name for map: ")
                if (not ("\nPlease enter a name or press the close button!" in self.bad_file_name_label_text)):
                    label.pack(pady=abs(20 - upper_bound_height))
                else:
                    label.pack(pady=abs(40 - upper_bound_height))
            elif (len(self.bad_file_name_label_text) == 0):
                popup.geometry(f"{400}x{150}")
                label = Label(popup, text="Enter a name for map: ")
                label.pack(pady=20)
        except (AttributeError):
            popup.geometry("400x150")
            label = Label(popup, text="Enter a name for map: ")
            label.pack(pady=20)
        
        

        entry = Entry(popup)
        entry.pack()

        def submit(event = None):
            self.file_name = entry.get()
            bad_input = False
            if (not bool(re.search(r"^[\w -]+$", self.file_name))):
                self.bad_file_name_label_text = f"The name \"{self.file_name}\" is invalid\n"
                self.bad_file_name_label_text += "Valid filenames must only contain 0-9, a-z, A-Z, spaces, -, or _"
                bad_input = True
            if (len(self.file_name) == 0):
                self.bad_file_name_label_text += "\nPlease enter a name or press the close button!"
                bad_input = True
            if (not bad_input):
                self.bad_file_name_label_text = ""
            
            if bad_input:
                self.export_failed = True
                self.root.attributes("-topmost", True)
                popup.attributes("-topmost", False)
                popup.destroy()
                try:
                    self.ask_name()
                except (ValueError):
                    return ""
            else:
                self.export_failed = False
                quiting()

        def quiting(event = None):
            
            popup.attributes("-topmost", False)
            self.root.attributes("-topmost", True)
            export_canceled = Toplevel(self.root)
            
            export_canceled.attributes("-type", "splash")
            export_canceled.attributes("-topmost", True)
            export_canceled.config(bg="black")
            if (self.export_failed or (len(self.file_name) == 0)):
                label = Label(export_canceled, text="Export canceled...",fg="white", bg=export_canceled.cget("bg"))
            else:
                label = Label(export_canceled, text="Export successful!",fg="white", bg=export_canceled.cget("bg"))
            export_canceled.geometry(f"{label.winfo_reqwidth()}x{label.winfo_reqheight()}")
            label.pack()
            
            
            popup.after(500, popup.destroy)
            export_canceled.wait_window(popup)
            export_canceled.attributes("-topmost", False)
            export_canceled.destroy()
            #popup.destroy()
            #raise ValueError("user terminated program")
            self.root.bind_all("<Escape>", lambda event: self.terminate_entire_program(event))
            return ""
        
        b = Button(popup, text="OK", command=submit).pack(pady=10)
        popup.bind("<Return>", submit)
        popup.grab_set()
        popup.bind_all("<Escape>", quiting)
        popup.protocol("WM_DELETE_WINDOW", quiting)
        
        self.root.wait_window(popup)
        

        if (len(self.file_name) == 0):
            raise ValueError("user terminated program")
        
        return self.file_name

    def export_shapes(self):
        exported_shapes = {"Rect":{}, "Circle":{}, "Oval":{}}
        for shape in self.shapes:
            if (shape.type == "rectangle"):
                exported_shapes["Rect"][shape.get_dims()] = shape.export_color
            elif (shape.type == "high-def oval"):
                for rect in shape.rects:
                    exported_shapes["Rect"][rect.get_dims()] = rect.export_color
            elif (shape.type == "oval"):
                exported_shapes["Oval"][shape.get_dims()] = shape.export_color
            elif (shape.type == "circle"):
                exported_shapes["Circle"][shape.get_dims()] = shape.export_color

        try:
            self.ask_name()
        except (ValueError):
            return
        
        with open(f"maps{self.file_nav_char}{self.file_name}.json", "w") as file:
            json.dump(exported_shapes, file, indent=4)

    def import_shapes(self):
        return

    def move_window_around(self, event):
        
        if (event.type.name == "ButtonPress"):
            self.window_event_x = event.x
            self.window_event_y = event.y
        if ((event.type.name == "Motion") and (event.state & state_masks["button1"])):
            dx = event.x - self.window_event_x
            dy = event.y - self.window_event_y
            x = self.root.winfo_x() + dx
            y = self.root.winfo_y() + dy

            #print(width, height)
            #mouse_pos = (event.x, event.y)
            #print(mouse_pos)
            self.root.geometry(f"+{x}+{y}")


    def force_keyboard_focus(self):
        self.root.focus_force()
        self.canvas.focus_set()

    def key_pressed(self, event):
        #print("KEY:", event.keysym, event.char, event.state)
        return

    def zoom_out(self):
        self.zoom_bool = not self.zoom_bool
        self.root.attributes("-zoomed", self.zoom_bool)

    def update_shape_type(self, event):

        self.current_shape_type = self.shape_selection.get(self.shape_selection.curselection()[0])
        # TODO handle rare-ish or occasional exception
    


    def fill_color_picker(self):
        self.shape_args["style"]["color"] = colorchooser.askcolor()
        if (not self.shape_args["style"]["color"][0]):
            self.shape_args["style"]["color"] = "grey90"
            self.shape_args["export"]["color"] = "(229, 229, 229, 255)"
            return
        self.shape_args["export"]["color"] = str(self.shape_args["style"]["color"][0] + (255,))
        self.shape_args["style"]["color"] = re.search(r"#\w+", str(self.shape_args["style"]["color"])).group(0)

    def outline_color_picker(self):
        self.shape_args["style"]["outline"] = colorchooser.askcolor()
        if (not self.shape_args["style"]["outline"][0]):
            self.shape_args["style"]["outline"] = "grey50"
            self.shape_args["export"]["outline"] = "(127, 127, 127, 255)"
            return
        self.shape_args["export"]["outline"] = str(self.shape_args["style"]["outline"][0] + (255,))
        self.shape_args["style"]["outline"] = re.search(r"#\w+", str(self.shape_args["style"]["outline"])).group(0)

    def radius_adjuster(self, event):
        if (self.system != "Linux"):
            if (hasattr(event, "delta") and event.delta):
                if event.delta > 0:
                    if (self.shape_args["oval"]["radius"] == 100):
                        return
                        self.shape_args["oval"]["radius"] += 1
                elif event.delta < 0:
                    if (self.shape_args["oval"]["radius"] == 0):
                        return
                    self.shape_args["oval"]["radius"] -= 1
        else:
            if (event.num == 4):
                if (self.shape_args["oval"]["radius"] == 100):
                    return
                self.shape_args["oval"]["radius"] += 1
            elif (event.num == 5):
                if (self.shape_args["oval"]["radius"] == 0):
                    return
                self.shape_args["oval"]["radius"] -= 1
        

    def undo_previous_shape(self, event):
        
        try:
            
            shape = self.shapes.pop()
            shape_type_popped = shape.type
            
            tag_name = shape_type_popped + " " + str(self.shape_counter[shape_type_popped])
            self.canvas.delete(tag_name)
            self.shape_counter[shape_type_popped] -= 1
            
            
        except (IndexError):
            return
    

    def end_dragging_button1(self, event):
        if event.state & state_masks["button1"]:
            self.canvas.delete("overlay")
            mouse_pos = (event.x, event.y)
            self.shape_args["rectangle"]["end"] = mouse_pos
            self.shape_args["oval"]["end"] = mouse_pos
            self.shape_args["high-def oval"]["end"] = mouse_pos

            #XXX RECTANGLE
            if (self.current_shape_type == "rectangle"):
                self.shape_counter["rectangle"] += 1
                self.canvas.create_rectangle(self.shape_args["rectangle"]["topleft"] + self.shape_args["rectangle"]["end"], 
                                             fill=self.shape_args["style"]["color"], outline=self.shape_args["style"]["outline"], 
                                             tags=(f"rectangle {self.shape_counter['rectangle']}",))
                self.shapes.append(Rect(**(self.shape_args["rectangle"] | self.shape_args["style"])))
                self.shapes[-1].export_color = self.shape_args["export"]["color"]
                self.shapes[-1].export_outline = self.shape_args["export"]["outline"]
            
            #XXX CIRCLE
            elif (self.current_shape_type == "circle"):
                self.shape_counter["circle"] += 1
               
                cx, cy = self.shape_args["circle"]["center"]
                x, y = mouse_pos
                dx = cx - x
                dy = cy - y
                radius = nint(math.dist((cx, cy), (x, y)))
                
                args = (cx - radius, cy - radius,cx + radius,cy + radius)
                self.canvas.create_oval(args,fill=self.shape_args["style"]["color"], outline=self.shape_args["style"]["outline"], 
                                        tags=(f"circle {self.shape_counter['circle']}",))
                self.shape_args["circle"]["end"] = (cx + radius,cy + radius)
                self.shapes.append(Oval(**(self.shape_args["circle"] | self.shape_args["style"])))

            #XXX OVAL
            elif (self.current_shape_type == "oval"):
                self.shape_counter["oval"] += 1
                self.canvas.create_oval(self.shape_args["oval"]["center"] + self.shape_args["oval"]["end"], 
                                             fill=self.shape_args["style"]["color"], outline=self.shape_args["style"]["outline"], 
                                             tags=(f"oval {self.shape_counter['oval']}",))
                self.shapes.append(Oval(**(self.shape_args["oval"] | self.shape_args["style"])))
                self.shapes[-1].export_color = self.shape_args["export"]["color"]
                self.shapes[-1].export_outline = self.shape_args["export"]["outline"]

            #XXX HIGHDEF OVAL
            elif (self.current_shape_type == "high-def oval"):
                self.shapes.append(HighDefOval(**(self.shape_args["high-def oval"] | self.shape_args["style"])))
                self.shape_counter["high-def oval"] += 1
                highdef_oval = self.shapes[-1]
                
                for rect in highdef_oval.rects:
                    rect.export_color = self.shape_args["export"]["color"]
                    rect.export_outline = self.shape_args["export"]["outline"]
                    self.canvas.create_rectangle(rect.topleft + rect.end, 
                                                 fill=self.shape_args["style"]["color"], outline=self.shape_args["style"]["outline"],
                                                 tags=(f"high-def oval {self.shape_counter['high-def oval']}",))
                

    def start_dragging_button1(self, event):
        if (event.type.name == "ButtonPress"):
            mouse_pos = (event.x, event.y)
            self.shape_args["rectangle"]["topleft"] = mouse_pos
            self.shape_args["oval"]["center"] = mouse_pos
            self.shape_args["circle"]["center"] = mouse_pos
            self.shape_args["high-def oval"]["center"] = mouse_pos
        if (event.state & state_masks["button1"]):
            self.canvas.delete("overlay")
            mouse_pos = (event.x, event.y)

            #XXX RECTANGLE OVERLAY
            if (self.current_shape_type == "rectangle"):
                self.canvas.create_rectangle(self.shape_args["rectangle"]["topleft"] + mouse_pos,fill=self.shape_args["style"]["color"], outline=self.shape_args["style"]["outline"], tags=("overlay",))
                
            #XXX OVAL OVERLAY
            elif (self.current_shape_type == "oval"):
                self.canvas.create_oval(self.shape_args["oval"]["center"] + mouse_pos,fill=self.shape_args["style"]["color"], outline=self.shape_args["style"]["outline"], tags=("overlay",))

            #XXX CIRCLE OVERLAY
            elif (self.current_shape_type == "circle"):
                cx, cy = self.shape_args["circle"]["center"]
                x, y = mouse_pos
                dx = cx - x
                dy = cy - y
                radius = nint(math.dist((cx, cy), (x, y)))
                args = (cx - radius, cy - radius,cx + radius,cy + radius)
                self.canvas.create_oval(args,fill=self.shape_args["style"]["color"], outline=self.shape_args["style"]["outline"], tags=("overlay",))

            #XXX HIGHDEF OVAL OVERLAY
            elif (self.current_shape_type == "high-def oval"):
                overlay_high_def_oval = HighDefOval(center=self.shape_args["high-def oval"]["center"], end=mouse_pos,
                                                    filled=self.shape_args["style"]["filled"], color=self.shape_args["style"]["color"],
                                                    outline=self.shape_args["style"]["outline"])
                for rect in overlay_high_def_oval.rects:
                    self.canvas.create_rectangle(rect.topleft + rect.end, 
                                                 fill=self.shape_args["style"]["color"], outline=self.shape_args["style"]["outline"],
                                                 tags=("overlay",))
                
        
    def bind_commands(self, widget, kw):
        for event, command in kw.items():
            widget.bind(event, command)

    def destroy(self, widget):
        widget.destroy()

    def run(self):
        self.root.update_idletasks()
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.focus_force()
        self.canvas.focus_set()
        self.root.mainloop()
        self.root.destroy()


DrawingBoard()
