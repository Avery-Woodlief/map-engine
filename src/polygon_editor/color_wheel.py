from tkinter import *
#from itertools import combinations, permutations
import colorsys
import json
import math
import os
import re




nint = lambda x: (math.floor(x + 0.5) + math.ceil((2*x - 1)/4) - math.floor((2*x - 1)/4) - 1) # nearest integer function


state_masks = {
                "button1":0x100,
                "button2":0x200,
                "button3":0x400,
                "motion":0x0
              }

class ColorWheelConfig:

    def __init__(self):
        self.pallete = {"frame" : {"x" : -1, "y":-1, "width":-1, "height":-1},
                        "canvas" : {"x" : -1, "y":-1, "width":-1, "height":-1}}
        self.mixture = {"frame" : {"x" : -1, "y":-1, "width":-1, "height":-1},
                        "canvas" : {"x" : -1, "y":-1, "width":-1, "height":-1}}


        self.branch = None
        self.current = None
        self.keys = ("pallete", "mixture", "frame", "canvas", "width", "height", "x", "y")

        self.colorwheel_config = {"pallete" : self.pallete,
                                  "mixture" : self.mixture}

        self.load_in_presets()


    def reset_current(self):
        self.current = self.colorwheel_config[self.branch]

    def __getitem__(self, key):
        if (key not in self.keys):
            raise KeyError(f"{key} not one of {self.keys}")

        if (key in ("pallete", "mixture")):
            self.current = self.colorwheel_config[key]   
            self.branch = key
            return self.current

        elif (((self.current == self.pallete) or (self.current == self.mixture)) and (self.current != None) and (key in ("frame", "canvas"))):
            self.current = self.current[key]
            return self.current

        elif (key in ("x", "y", "width", "height") and (self.current != None)):
            self.current = self.current[key]
            return self.current

        

    def __setitem__(self, key, value):
        if (not isinstance(value, (int, str))):
            raise ValueError(f"{self} only takes values of type int or str, got one of type {type(value)}")
        if (key in ("pallete", "mixture", "frame", "canvas")):
            raise KeyError(f"key {key} is not editable in {self}")

        if ((self.current != self.pallete["frame"]) and (self.current != self.pallete["canvas"])) and ((self.current != self.mixture["frame"]) and (self.current != self.mixture["canvas"])):
            raise ValueError("self.current must be set to either self.pallete(['frame'] or ['canvas']) or self.mixture(['frame'] or ['canvas'])")

        self.current[key] = value
        

    def update_colorwheel_config_part(self):
        with open("color_wheel_config.json", "w") as file:
            json.dump(self.colorwheel_config, file, indent=4)
        file.close()

    def load_in_presets(self):
        with open("color_wheel_config.json", "r") as file:
            self.colorwheel_config = json.load(file)
            self.pallete = self.colorwheel_config["pallete"]
            self.mixture = self.colorwheel_config["mixture"]
        file.close()

class ColorWheel:

    def __init__(self, parent):

        self.config = ColorWheelConfig()

        self.parent = parent
        self.pallete_frame = Frame(self.parent, width=self.config["pallete"]["frame"]["width"], 
                                                height=self.config["pallete"]["frame"]["height"], name="pallete_frame")
        self.pallete_frame.place(x=self.config["pallete"]["frame"]["x"], 
                                 y=self.config["pallete"]["frame"]["y"])

        self.pallete_frame.update_idletasks()
        self.pallete_canvas = Canvas(self.pallete_frame, width=self.config["pallete"]["canvas"]["width"], 
                                                         height=self.config["pallete"]["canvas"]["height"], name="pallete_canvas")
        self.pallete_canvas.update_idletasks()

        self.mixture_frame = Frame(self.parent, width=self.config["mixture"]["frame"]["width"], 
                                                height=self.config["mixture"]["frame"]["height"], name="mixture_frame")
        self.mixture_frame.place(x=self.config["mixture"]["frame"]["x"], 
                                 y=self.config["mixture"]["frame"]["y"])
        self.mixture_frame.update_idletasks()      
        self.mixture_canvas = Canvas(self.mixture_frame, width=self.config["mixture"]["canvas"]["width"], 
                                                         height=self.config["mixture"]["canvas"]["height"], name="mixture_canvas")
        self.mixture_canvas.update_idletasks()


        
        

        self.pallete_radius = nint(self.pallete_frame["width"]/2) - 5
        self.pallete_center = (5 + self.pallete_radius, nint(self.pallete_frame["height"]/2))

        self.mixture_radius = nint(self.mixture_frame["width"]/2) - 2
        self.mixture_center = (2 + self.mixture_radius, nint(self.mixture_frame["height"]/2))

        self.pallete_canvas.place(x=0, y=0)
        self.mixture_canvas.place(x=0, y=0)

        self.selected_canvas = self.pallete_canvas
        self.selected_frame = self.pallete_frame
        
        self.colors = []
        self.mixture = []
        self.draw_mixture()

        self.base_reds = []
        self.base_greens = []
        self.base_blues = []

        # COLORWHEEL CURSOR

        self.cursor_radius = 5
        self.cursor = None

        #

        self.positions = {"red":1, "green":2, "blue":3}


        self.color_operation = None
        self.inspect_mode_enabled = False
        self.color_anchor = ""

        custom_circle_args_pallete = (self.pallete_center[0] - self.pallete_radius, self.pallete_center[1] - self.pallete_radius,
                                      self.pallete_center[0] + self.pallete_radius, self.pallete_center[1] + self.pallete_radius)


        custom_circle_args_mixture = (self.mixture_center[0] - self.mixture_radius, self.mixture_center[1] - self.mixture_radius,
                                      self.mixture_center[0] + self.mixture_radius, self.mixture_center[1] + self.mixture_radius)

        self.pallete_canvas.create_oval(custom_circle_args_pallete, outline="white", w=5, tags=("pallete",))
        self.mixture_canvas.create_oval(custom_circle_args_mixture, outline="white", w=2, tags=("mixture",))


        

        self.generate_colors()
        
        self.draw_pallete()
        self.color_anchor_bind_id_B3 = self.parent.bind("<ButtonPress-3>", self.select_color_anchor, add="+")
        self.color_picker_bind_id_B1 = self.parent.bind("<ButtonPress-1>", self.color_picker, add="+")
        self.color_picker_bind_id_Motion = self.parent.bind("<Motion>", self.color_picker, add="+")
        self.color_operator_bind_id_KP = self.parent.bind("<KeyPress>", self.color_operator, add="+")
        self.inspect_color_bind_id_Motion = self.parent.bind("<Motion>", self.inspect_color, add="+")


        self.moving_widget_bind_id_Motion = self.parent.bind("<Motion>", self.moving_widget, add="+")
        self.mousewheel_bind_id_B4 = self.parent.bind("<Button-4>", self.mousewheel, add="+")
        self.mousewheel_bind_id_B5 = self.parent.bind("<Button-5>", self.mousewheel, add="+")
        #self.parent.bind("<MouseWheel>", self.mousewheel)

    def update_config(self, frame, canvas):

        self.config["frame"]
        self.config["x"] = str(frame.winfo_x())
        self.config["y"] = str(frame.winfo_y())
        self.config["width"] = str(frame.winfo_width())
        self.config["height"] = str(frame.winfo_height())

        self.config.reset_current()

        self.config["canvas"]
        self.config["x"] = str(canvas.winfo_x())
        self.config["y"] = str(canvas.winfo_y())
        self.config["width"] = str(canvas.winfo_width())
        self.config["height"] = str(canvas.winfo_height())

        self.config.reset_current()

    def find_closest(self, event):
        if (event.widget == self.pallete_canvas):
            return self.pallete_canvas.find_closest(event.x, event.y)
        elif (event.widget == self.mixture_canvas):
            return self.mixture_canvas.find_closest(event.x, event.y)

        return None

    def mousewheel(self, event):

        if (self.selected_frame == None or self.selected_canvas == None):
            return

        if event.num == 4:
            self.selected_frame["width"] += 5
            self.selected_frame["height"] += 5
            

        elif event.num == 5:
            self.selected_frame["width"] -= 5
            self.selected_frame["height"] -= 5

        if (event.num in (4, 5)):
            self.selected_canvas.config(width=self.selected_frame["width"], height=self.selected_frame["height"])
            self.selected_canvas.update_idletasks()
            self.selected_frame.update_idletasks()

        if (self.selected_frame == self.pallete_frame):
            self.config["pallete"]
        elif (self.selected_frame == self.mixture_frame):
            self.config["mixture"]

        

        if (event.num in (4, 5)):
            self.update_config(self.selected_frame, self.selected_canvas)
            #print(self.config.colorwheel_config)
            self.config.update_colorwheel_config_part()

        if (event.num in (4, 5) and self.selected_canvas == self.pallete_canvas):
            self.pallete_canvas.delete("pallete")

            self.pallete_radius = nint(self.pallete_frame["width"]/2) - 5
            self.pallete_center = (5 + self.pallete_radius, nint(self.pallete_frame["height"]/2))
            custom_circle_args_pallete = (self.pallete_center[0] - self.pallete_radius, self.pallete_center[1] - self.pallete_radius,
                                          self.pallete_center[0] + self.pallete_radius,self.pallete_center[1] + self.pallete_radius)
            self.pallete_canvas.create_oval(custom_circle_args_pallete, outline="white", w=5, tags=("pallete",))
            self.pallete_canvas.delete("pallete color")
            self.draw_pallete()

            

        elif (event.num in (4, 5) and self.selected_canvas == self.mixture_canvas):
            self.mixture_canvas.delete("mixture")

            self.mixture_radius = nint(self.mixture_frame["width"]/2) - 2
            self.mixture_center = (2 + self.mixture_radius, nint(self.mixture_frame["height"]/2))
            custom_circle_args_mixture = (self.mixture_center[0] - self.mixture_radius, self.mixture_center[1] - self.mixture_radius,
                                          self.mixture_center[0] + self.mixture_radius, self.mixture_center[1] + self.mixture_radius)
            self.mixture_canvas.create_oval(custom_circle_args_mixture, outline="white", w=2, tags=("mixture",))            
            self.mixture_canvas.delete("mixture color")            
            self.draw_mixture()
        

    def moving_widget(self, event):
        if (self.selected_frame == None):
            return
            
        if (event.type.name == "Motion" and bool(re.search(r"state=Shift\|Button3", str(event)))):
            x_ = event.x
            y_ = event.y
            #self.selected_canvas.place(x=x_, y=y_)
            self.selected_frame.place(x=x_, y=y_)

            
            if (self.selected_frame == self.pallete_frame):
                self.config.branch = "pallete"
                self.config.reset_current()
                self.config["pallete"]
            elif (self.selected_frame == self.mixture_frame):
                self.config.branch = "mixture"
                self.config.reset_current()
                self.config["mixture"]
            self.update_config(self.selected_frame, self.selected_canvas)
            self.config.update_colorwheel_config_part()
            
            

    def dist_from_white(self, hex_color):
        return math.dist(self.hex_to_rgb(hex_color), self.hex_to_rgb('#ffffff'))

    def dist_from_black(self, hex_color):
        return math.dist(self.hex_to_rgb(hex_color), self.hex_to_rgb('#000000'))


    def inspect_color(self, event):

        if (self.inspect_mode_enabled):
        
            item = self.find_closest(event)#self.pallete_canvas.find_closest(event.x, event.y) #XXX
            if not item:
                return

            tags = None
            if (event.widget == self.pallete_canvas):
                tags = self.pallete_canvas.gettags(item[0])
            elif (event.widget == self.mixture_canvas):
                tags = self.mixture_canvas.gettags(item[0])

            if tags == None:
                return
            for tag in tags:
                if tag.startswith("#"):
                    os.system("clear")
                    print(tag)


    def select_color_anchor(self, event):
        
        item = self.find_closest(event)#self.pallete_canvas.find_closest(event.x, event.y) #XXX
        
        cx = event.x
        cy = event.y
        rad = 5
        if not item:
            return

        tags = None
        if (event.widget == self.pallete_canvas):
            tags = self.pallete_canvas.gettags(item[0])
        elif (event.widget == self.mixture_canvas):
            tags = self.mixture_canvas.gettags(item[0])

        if tags == None:
            return

        for tag in tags:
            if tag.startswith("#"):
                
                
                self.color_anchor = tag
                if (event.widget == self.pallete_canvas):
                    self.mixture_canvas.delete("color anchor")
                    self.pallete_canvas.delete("color anchor")
                    self.pallete_canvas.create_oval((cx - rad, cy - rad, cx + rad, cy + rad), fill="#aeaeae", outline="white", 
                                                    w=1, tags=(tag, "color anchor",))
                elif (event.widget == self.mixture_canvas):
                    self.pallete_canvas.delete("color anchor")
                    self.mixture_canvas.delete("color anchor")
                    self.mixture_canvas.create_oval((cx - rad, cy - rad, cx + rad, cy + rad), fill="#aeaeae", outline="white", 
                                                    w=1, tags=(tag, "color anchor",))
                return

    def color_operator(self, event):
        if (event.char == "+"):
            self.color_operation = self.add_colors
        elif (event.char == "-"):
            self.color_operation = self.subtract_colors
        elif (event.char == "*"):
            self.color_operation = self.multiply_colors

        if (event.char == "i" or event.char == "I"):
            self.inspect_mode_enabled = not self.inspect_mode_enabled

    def mouse_in_pallete(self, event):
        return ((event.x - self.pallete_center[0])**2) + ((event.y - self.pallete_center[1])**2) <= (self.pallete_radius**2)

    def mouse_in_mixture(self, event):
        return ((event.x - self.mixture_center[0])**2) + ((event.y - self.mixture_center[1])**2) <= (self.mixture_radius**2)

    def color_picker(self, event):
        # check to avoid conflicts with other binds
        #print(hex(event.state))
        #print(hex(0x400 | 0x1))
        
        cx = event.x
        cy = event.y

        if (event.widget == self.pallete_canvas):#".!frame.!canvas"): # pallete canvas
            #print("in pallete canvas")
            if (self.mouse_in_pallete(event)):
                self.mixture_canvas.config(cursor="none")
                self.mixture_canvas.delete("cursor")
                self.pallete_canvas.config(cursor="none")
                self.pallete_canvas.delete("cursor")
                self.cursor = self.pallete_canvas.create_oval((cx - self.cursor_radius, cy - self.cursor_radius, 
                                                       cx + self.cursor_radius, cy + self.cursor_radius),
                                                      outline="white", tags=("cursor",))

            else:
                self.pallete_canvas.config(cursor="arrow")

        elif (event.widget == self.mixture_canvas):#".!frame2.!canvas"):
            #print("in mixture canvas")
            if (self.mouse_in_mixture(event)):
                self.pallete_canvas.config(cursor="none")
                self.pallete_canvas.delete("cursor")
                self.mixture_canvas.config(cursor="none")
                self.mixture_canvas.delete("cursor")
                self.cursor = self.mixture_canvas.create_oval((cx - self.cursor_radius, cy - self.cursor_radius, 
                                                       cx + self.cursor_radius, cy + self.cursor_radius),
                                                      outline="white", tags=("cursor",))
            else:
                self.mixture_canvas.config(cursor="arrow")
        else:
            self.pallete_canvas.config(cursor="none")
            self.pallete_canvas.delete("cursor")
            self.mixture_canvas.config(cursor="none")
            self.mixture_canvas.delete("cursor")
            #print("in root")
        
        if ((event.type.name == "Motion" and (event.state & state_masks["button1"])) or (event.type.name == "ButtonPress")):
            
            item = self.find_closest(event)#self.pallete_canvas.find_closest(event.x, event.y) #XXX
            if not item:
                return
            tags = None
            if (event.widget == self.pallete_canvas):
                tags = self.pallete_canvas.gettags(item[0])
            elif (event.widget == self.mixture_canvas):
                tags = self.mixture_canvas.gettags(item[0])

            if tags == None:
                return
            
            for tag in tags:
                if tag.startswith("#"):
                    if (self.color_operation != None and (len(self.color_anchor) > 0)):
                        added_color = self.color_operation(self.color_anchor, tag)

                        
                        self.mixture.append(added_color)

                        self.mixture = list(set(self.mixture))
                        self.mixture.sort(key=self.hex_to_hue)
                        
                        self.draw_mixture()
                        if (event.widget == self.mixture_canvas and self.mouse_in_mixture(event)):
                            
                            self.mixture_canvas.config(cursor="none")
                            self.mixture_canvas.delete("cursor")
                            self.cursor = self.mixture_canvas.create_oval((cx - self.cursor_radius, cy - self.cursor_radius, 
                                                                   cx + self.cursor_radius, cy + self.cursor_radius),
                                                                  outline="white", tags=("cursor",))


                            

    def draw_pallete(self):
        i = 0
        if (len(self.colors) == 0):
            return
        increment = (1/len(self.colors))*-360 # when gets to last color, deg should be 360
        for color in self.colors:
            self.pallete_canvas.create_line(self.pallete_center, 
                                   (self.pallete_center[0] + (self.pallete_radius*math.cos(math.radians(i))),
                                    self.pallete_center[1] + (self.pallete_radius*math.sin(math.radians(i)))),
                                   width=5, fill=color, tags=(color,"pallete color",))
            i += increment

    def get_items_with_intersecting_tags(self, tags):
        items = []
        for tag in tags:
            items.append(set(self.pallete_canvas.find_withtag(tag)))

        return set.intersection(*items)

    def get_circle_args_from_oval(self, center, radius):
        return (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius)

    def update_anchor_in_mixture(self, angle):
        ref_center = [self.mixture_center[0] + ((self.mixture_radius - 5)*math.cos(angle)), 
                      self.mixture_center[1] + ((self.mixture_radius - 5)*math.sin(angle))]
        

        update_center = self.restrict_mixture_anchor_to_line(tuple(ref_center), (self.mixture_center[0], self.mixture_center[1], ref_center[0], ref_center[1]))

        return self.get_circle_args_from_oval(update_center, 5)

    def restrict_mixture_anchor_to_line(self, anchor_center, line_coords):
        cx, cy = anchor_center # radius of anchor known to be 5
        x1, y1, x2, y2 = line_coords



        cx = nint((x2 + x1)/2)
        cy = nint((y1 + y2)/2)

        return (cx, cy)
        

    def draw_mixture(self):
        self.mixture_canvas.delete("mixture color")
        i = 0
        if (len(self.mixture) == 0):
            return
        increment = (1/len(self.mixture))*-360 # when gets to last color, deg should be 360
        for color in self.mixture:
            if (nint(360/len(self.mixture)) < 5):
                line_width = 5
            else:
                line_width = nint(360/len(self.mixture))
            
            self.mixture_canvas.create_line(self.mixture_center, 
                                   (self.mixture_center[0] + ((self.mixture_radius - 5)*math.cos(math.radians(i))),
                                    self.mixture_center[1] + ((self.mixture_radius - 5)*math.sin(math.radians(i)))),
                                    width=line_width, fill=color, tags=(color,"mixture color"))
            if (color == self.color_anchor):
                
                self.mixture_canvas.delete("color anchor")
                self.mixture_canvas.create_oval(self.update_anchor_in_mixture(math.radians(i)), outline="white", 
                                        fill="#aeaeae", w=1, tags=(self.color_anchor, "color anchor",))
                

                
                
            i += increment

    def clean_up_color_wheel(self, color):
        while (self.colors.count(color) > 1):
            self.colors.remove(color)

    def generate_reds(self):
        for r in range(0, 255 + 1): # [0, 256) in integers = [0, 255]
             
            color = "#" + f"{max(0, min(255, r)):02x}" + "00" + "00"
            self.base_reds.append(color)
        self.base_reds = self.base_reds[self.base_reds.index("#000000"):]

        self.base_reds.sort(key=self.red)

    def generate_greens(self):
        for g in range(0, 255 + 1): # [0, 256) in integers = [0, 255]
            
            color = "#" + "00" + f"{max(0, min(255, g)):02x}" + "00"
            self.base_greens.append(color)
        self.base_greens = self.base_greens[self.base_greens.index("#000000"):]
        self.base_greens.sort(key=self.green)

    def generate_blues(self):
        for b in range(0, 255 + 1): # [0, 256) in integers = [0, 255]

            color = "#" + "00" + "00" + f"{max(0, min(255, b)):02x}"
            self.base_blues.append(color)
        self.base_blues = self.base_blues[self.base_blues.index("#000000"):]
        self.base_blues.sort(key=self.blue)
            

    def get_red_channel(self, hex_color):
        red = re.search(r"(?<=#)\w+(?=0000)", hex_color)
        if (not (red == None)):
            return red.group(0)
        return None

    def get_green_channel(self, hex_color):
        green = re.search(r"(?<=#00)\w+(?=00)", hex_color)
        if (not (green == None)):
            return green.group(0)
        return None

    def get_blue_channel(self, hex_color):
        blue = re.search(r"(?<=#0000)\w+", hex_color)
        if (not (blue == None)):
            return blue.group(0)
        return None

    def get_part(self, color_channel, positions):
        start, end = positions
        if (end >= 0):
            if (color_channel == "red"):
                return self.base_reds[start: end]
            elif (color_channel == "green"):
                return self.base_greens[start:end]
            elif (color_channel == "blue"):
                return self.base_blues[start:end]
        else:
            if (color_channel == "red"):
                return self.base_reds[start:]
            elif (color_channel == "green"):
                return self.base_greens[start:]
            elif (color_channel == "blue"):
                return self.base_blues[start:]
        return None

    def val_to_hex(self, val):
        return f"{max(0, min(255, val)):02x}"

    def mix(self, color_from, color_to):
        color_from_vals = self.get_bulk_channel_part(color_from)
        color_to_vals = self.get_bulk_channel_part(color_to)

        color_from_vals.sort(reverse=True)
        color_to_vals.sort()

        pos_from = self.positions[color_from]
        pos_to = self.positions[color_to]
        if (pos_from == pos_to):
            return
        missed_pos = None
        for k in self.positions.keys():
            if (k == color_from):
                continue
            elif (k == color_to):
                continue
            else:
                missed_pos = k
                break

        positions = [pos_from, pos_to, self.positions[missed_pos]]
        positions.sort() # says which positions are for red, green, and blue channels, resp.

        channel_placements = {positions[0] : "00",
                              positions[1] : "00",
                              positions[2] : "00"} # this allows the use for the sorted positions

        def build_color():
            return "#" + channel_placements[positions[0]] + channel_placements[positions[1]] + channel_placements[positions[2]]

        colors_added = []

        
        for i, j in zip(color_from_vals, color_to_vals):
            t_i = i - 1
            
            t_j = j + 1

            if (t_i < 0 or t_j > 255):
                break
            channel_placements[pos_from] = self.val_to_hex(t_i)
            channel_placements[pos_to] = self.val_to_hex(t_j)

            color = build_color()
            #colors_added.append(self.add_colors(c, color))
            colors_added.append(color)
        
        return colors_added
        

    def add_colors(self, color_a, color_b):
        if (color_a == None or color_b == None):
            return
        r_a, g_a, b_a = self.hex_to_rgb(color_a)
        r_b, g_b, b_b = self.hex_to_rgb(color_b)

        r = (r_a + r_b) % 256
        g = (g_a + g_b) % 256
        b = (b_a + b_b) % 256

        color = "#" + self.val_to_hex(r) + self.val_to_hex(g) + self.val_to_hex(b)
        return color

    def subtract_colors(self, color_a, color_b):
        if (color_a == None or color_b == None):
            return
        r_a, g_a, b_a = self.hex_to_rgb(color_a)
        r_b, g_b, b_b = self.hex_to_rgb(color_b)

        r = (r_a - r_b) % 256
        g = (g_a - g_b) % 256
        b = (b_a - b_b) % 256

        color = "#" + self.val_to_hex(r) + self.val_to_hex(g) + self.val_to_hex(b)
        return color

    def multiply_colors(self, color_a, color_b):
        if (color_a == None or color_b == None):
            return
        r_a, g_a, b_a = self.hex_to_rgb(color_a)
        r_b, g_b, b_b = self.hex_to_rgb(color_b)

        r = (r_a * r_b) % 256
        g = (g_a * g_b) % 256
        b = (b_a * b_b) % 256

        color = "#" + self.val_to_hex(r) + self.val_to_hex(g) + self.val_to_hex(b)
        return color

    def get_bulk_channel_part(self, base_color):
        base_vals = []
        if (base_color == "red"):
            
            for color in self.base_reds:
                base_vals.append(int(f"0x{self.get_red_channel(color)}", 16))

        elif (base_color == "green"):
            for color in self.base_greens:
                base_vals.append(int(f"0x{self.get_green_channel(color)}", 16))

        elif (base_color == "blue"):
            for color in self.base_blues:
                base_vals.append(int(f"0x{self.get_blue_channel(color)}", 16))
        return base_vals

    def generate_colors(self):
        
        self.generate_reds()
        self.generate_greens()
        self.generate_blues()


        self.colors += self.mix("red", "blue")
        self.colors += self.mix("red", "green")
        self.colors += self.mix("blue", "green")

        self.colors.sort(key=self.hex_to_hue)

    def red(self, hex_color):
        return -self.hex_to_rgb(hex_color)[0]

    def green(self, hex_color):
        return self.hex_to_rgb(hex_color)[1]

    def blue(self, hex_color):
        return self.hex_to_rgb(hex_color)[2]

    def RG(self, hex_color):
        return (self.hex_to_rgb(hex_color)[0], self.hex_to_rgb(hex_color)[1])

    def GB(self, hex_color):
        return (self.hex_to_rgb(hex_color)[1], self.hex_to_rgb(hex_color)[2])

    def RB(self, hex_color):
        return (self.hex_to_rgb(hex_color)[0], self.hex_to_rgb(hex_color)[2])

    def RGB(self, hex_color):
        return (self.hex_to_rgb(hex_color)[0], self.hex_to_rgb(hex_color)[1], self.hex_to_rgb(hex_color)[2])

    def remove_colors_closest_to(self, hex_color, target, min_dist):
        if (math.dist(self.hex_to_rgb(hex_color), self.hex_to_rgb(target)) < min_dist):
            self.colors.remove(hex_color)
    
        
    def hexsum(self, string):
        sum_=0
        
        channels=re.findall(r"\w\w", string)
        for i in range(len(channels)):
            channels[i] = int(hex(eval("0x"+channels[i])), 16)
        return max(channels)

    def hex_to_rgb(self, hex_color):
        if (hex_color == None):
            return
        hex_color = hex_color.lstrip("#")

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)

    def hex_to_hsv(self, hex_color):
        if (hex_color == None):
            return
        r, g, b = self.hex_to_rgb(hex_color)

        return (colorsys.rgb_to_hsv(r / 255,g / 255,b / 255)[0],
               -colorsys.rgb_to_hsv(r / 255,g / 255,b / 255)[1],
               -colorsys.rgb_to_hsv(r / 255,g / 255,b / 255)[2])

    def hex_to_hue(self, hex_color):
        if (hex_color == None):
            return
        r, g, b = self.hex_to_rgb(hex_color)

        return (colorsys.rgb_to_hsv(r / 255,g / 255,b / 255)[0])

    def hex_to_saturation(self, hex_color):
        if (hex_color == None):
            return
        r, g, b = self.hex_to_rgb(hex_color)

        return (colorsys.rgb_to_hsv(r / 255,g / 255,b / 255)[1]) 

    def luminance(self, hex_color):
        if (hex_color == None):
            return
        r, g, b = self.hex_to_rgb(hex_color)

        r /= 255
        g /= 255
        b /= 255

        def linearize(c):
            if c <= 0.04045:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4

        r = linearize(r)
        g = linearize(g)
        b = linearize(b)

        return (
            0.2126 * r +
            0.7152 * g +
            0.0722 * b
        )
