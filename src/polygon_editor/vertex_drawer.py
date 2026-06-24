from tkinter import *
import _tkinter
import math
import os
import json

nint = lambda x: (math.floor(x + 0.5) + math.ceil((2*x - 1)/4) - math.floor((2*x - 1)/4) - 1) # nearest integer function

state_masks = {
                "button1":0x100,
                "button2":0x200,
                "button3":0x400,
                "motion":0x0
              }

def draw_grid_lines(canvas, space_x, space_y, width, height, offset_x=0, offset_y=0):
    if space_x <= 0 or space_y <= 0:
        return

    # Draw only visible grid lines, shifted by the pan offsets.
    start_y = offset_y % space_y
    y = start_y
    while y <= height:
        canvas.create_line(0, y, width, y, fill="black", tags=("h-line",))
        y += space_y

    start_x = offset_x % space_x
    x = start_x
    while x <= width:
        canvas.create_line(x, 0, x, height, fill="black", tags=("v-line",))
        x += space_x


class Cursor:
    def __init__(self):
        self.x = 0
        self.y = 0


class Point:

    def __init__(self, x, y, tag):
        self.x = x
        self.y = y
        self.tag = tag
        self.col = None
        self.row = None # relative to parent grid
        self.rel_col = None
        self.rel_row = None # relative to anchor point

    def __iter__(self):
        yield self.x
        yield self.y

    def __eq__(self, other):
        if (self.x == other.x and self.y == other.y and self.tag == other.tag):
            return True
        return False

    def __str__(self):
        return f"({self.col}, {self.row})"


class SmartList:

    def __init__(self, values : list):
        if (len(values) < 3):
            raise ValueError("not enough values to be a 'SmartList'")
        self.values = values
        self.current_value = self.values[0]
        self.previous_value = self.values[(- 1) % len(self.values)]
        self.next_value = self.values[(1) % len(self.values)]

    def shift(self, index):
        if (not isinstance(index, int)):
            raise IndexError("index is not of type int")
        self.current_value = self.values[index]
        self.previous_value = self.values[(index - 1) % len(self.values)]
        self.next_value = self.values[(index + 1) % len(self.values)]

    def current(self):
        c = self.current_value
        index = self.values.index(c)
        self.shift(index)
        self.current_value = self.next_value
        return c
    def next(self):
        n = self.next_value
        index = self.values.index(n)
        self.shift(index)
        return n

class Polygon:

    def __init__(self, parent, color, tag, points=None):
        if points is None:
            points = []
        for p in points:
            if not isinstance(p, Point):
                return TypeError("\nfound a value in self.points not of type Point\nInstead was of type {type(p)}\n")
        self.parent = parent
        self.points = points
        self.flattened_points = []
        self.color = color
        self.tag = tag
        self.anchor = 0

    def __setitem__(self, index, value):
        if (index >= len(self.points)):
            self.points.insert(index, value)
            return
        self.points[index] = value
    def __getitem__(self, index):
        if (index >= len(self.points)):
            return None
        return self.points[index]

    def anchor_point(self, point):
        if (self[self.anchor] == point):
            self[self.anchor].rel_col = 0
            self[self.anchor].rel_row = 0

        point.rel_col = point.col - self[self.anchor].col
        point.rel_row = point.row - self[self.anchor].row

    def get_rel_point(self, point):
        try:
            _ = self.points.index(point)
        except(IndexError, ValueError):
            return None

        return (point.col - self[self.anchor].col, point.row - self[self.anchor].row)

    def flatten_points(self):
        self.flattened_points = []
        for point in self.points:
            # Preserve polygon geometry in grid coordinates.
            # Only convert col/row -> screen x/y when drawing.
            x = self.parent.grid.offset_x + (point.col * self.parent.grid.space_x)
            y = self.parent.grid.offset_y + (point.row * self.parent.grid.space_y)
            point.x = x
            point.y = y
            self.flattened_points.append(x)
            self.flattened_points.append(y)

    def update_anchor(self):
        try:
            self[self.anchor].col, self[self.anchor].row = self.parent.clamp_point((self[self.anchor].x, self[self.anchor].y))

        except (AttributeError):
            return

    def clamp_points(self):
        if (len(self.points) == 0):
            raise IndexError("no points to clamp")
        
        for point in self.points:
            col, row = self.parent.clamp_point((point.x, point.y))
            
            point.x = (col) * self.parent.grid.space_x
            point.y = (row) * self.parent.grid.space_y
                

    def redraw(self):
        if (len(self.points) == 0):
            return

        # Do NOT reclamp points while zooming.
        # The stable data is point.col / point.row.
        self.flatten_points()

        self.parent.grid.canvas.delete(self.tag)
        self.parent.grid.canvas.create_polygon(self.flattened_points, fill=self.color, tags=(self.tag,))

    
    def __str__(self):
        output = f"{self.points[0]}"
        for i in range(1, len(self.points)):
            output += f", {self.points[i]}"

        return output
        
        
class Grid:

    def __init__(self, parent):
        #self.root = Tk()
        #self.root.geometry("500x500")
        self.base_space_x = 10
        self.base_space_y = 10

        # Current screen spacing. These are derived from base spacing * zoom_scale.
        # They should not be repeatedly rounded and multiplied, because that causes
        # zoom drift and breaks clean zoom-in / zoom-out behavior.
        self.space_x = self.base_space_x
        self.space_y = self.base_space_y

        self.zoom_scale = 1.0
        self.zoom_step = 1.25
        self.min_zoom_scale = 0.20
        self.max_zoom_scale = 48.00

        # Pan offset in screen pixels. Geometry still lives in grid col/row values.
        self.offset_x = 0
        self.offset_y = 0

        self.parent = parent
        self.canvas = Canvas(self.parent.root, width=self.parent.winfo_width(), height=self.parent.winfo_height(), bg="white")
        self.canvas.bind_all("<KeyPress>", self.zoom)
        self.path = str(self.canvas)

    def update_spacing(self):
        self.space_x = max(1, nint(self.base_space_x * self.zoom_scale))
        self.space_y = max(1, nint(self.base_space_y * self.zoom_scale))
        #print(f"space_x: {self.space_x}, space_y: {self.space_y}")

    def apply_zoom(self, direction, anchor_x=None, anchor_y=None):
        old_space_x = self.space_x
        old_space_y = self.space_y

        if (direction > 0):
            self.zoom_scale *= self.zoom_step
        elif (direction < 0):
            self.zoom_scale /= self.zoom_step
        else:
            return

        self.zoom_scale = max(self.min_zoom_scale, min(self.zoom_scale, self.max_zoom_scale))
        self.update_spacing()

        # If an anchor point is given, keep the same grid/world location
        # under that screen point while zooming.
        if (anchor_x is not None and anchor_y is not None):
            world_x = (anchor_x - self.offset_x) / old_space_x
            world_y = (anchor_y - self.offset_y) / old_space_y

            self.offset_x = anchor_x - (world_x * self.space_x)
            self.offset_y = anchor_y - (world_y * self.space_y)

        self.redraw(event=None)

    def zoom(self, event):
        if (event.char in ("+", "=")):
            self.apply_zoom(1)
        elif (event.char == "-"):
            self.apply_zoom(-1)

        return

    def pack(self, kw):
        argument_string = f"{list(kw.keys())[0]}=" + f"\"{kw[list(kw.keys())[0]]}\""
        for i in range(1, len(list(kw.keys()))):
            argument_string += f", {list(kw.keys())[i]}={kw[list(kw.keys())[i]]}"
        eval(f"self.canvas.pack({argument_string})")
        #self.canvas.update_idletasks()

    def redraw(self, event):
        self.canvas.delete("all")
        draw_grid_lines(
            self.canvas,
            self.space_x,
            self.space_y,
            self.parent.winfo_width(),
            self.parent.winfo_height(),
            self.offset_x,
            self.offset_y
        )
        self.parent.redraw()


class Graph:

    def __init__(self, init_width, init_height, parent):


        if (not (isinstance(init_width, int) and isinstance(init_height, int))):
            raise ValueError(f"both init graph width and init graph height are bad types, got type {type(init_width)} and {type(init_height)}")
        elif (not (init_width > 0 and init_height > 0)):
            raise ValueError(f"neither init graph width nor init graph height are positive integers")
        elif (not (init_width > 0)):
            raise ValueError("init graph width is not positive integer")
        elif (not (init_height > 0)):
            raise ValueError("init graph height is not positive integer")
        elif (not isinstance(init_width, int)):
            raise ValueError(f"bad init graph width type, got {type(init_width)}")
        elif (not isinstance(init_height, int)):
            raise ValueError(f"bad init graph height type, got {type(init_height)}")

        self.parent = parent
        self.root = Frame(self.parent, width=init_width, height=init_height, takefocus=True)
        
        self.path = str(self.root)
        self.root.grid(column=1, row=0, sticky="nwe")#.pack(side="right")#side="top", ipadx=100, pady=100
        self.root.focus_set()
        self.has_focus = True
        #self.root = Tk()
        
        #self.root.geometry(f"{init_width}x{init_height}")
        self.root.update_idletasks()
        
        #self.graph_points = []
        self.selected_polygon = 0
        self.polygons = [Polygon(self, "black", f"polygon - {i + 1}") for i in range(9)]
        
        self.grid = Grid(self)
        self.grid.pack({"fill":"both", "expand":True})
        self.grid.redraw(event=None)
        self.root.update_idletasks()
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.pan_origin_x = 0
        self.pan_origin_y = 0
        

        self.root.bind("<KeyPress>", self.select_polygon, add="+")

        # Press V to show/hide the blue polygon vertices.
        # The polygon itself stays visible.
        self.show_vertices = True

        self.root.bind("<Configure>", self.grid.redraw)
        self.root.bind("<Escape>", self.end_program)
        self.root.bind("v", self.toggle_vertices)
        self.root.bind("V", self.toggle_vertices)
        #self.root.bind("<Motion>", self.clamp_cursor)
        self.grid.canvas.bind("<Motion>", self.clamp_cursor)

        # Left click and drag pans the view.
        #self.root.bind("<ButtonPress-1>", self.start_pan)
        #self.root.bind("<B1-Motion>", self.pan)
        self.grid.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.grid.canvas.bind("<B1-Motion>", self.pan)
        self.grid.canvas.bind("<ButtonRelease-1>", self.end_pan)

        # Right click places points now, because Button-1 is used for panning.
        #self.root.bind("<ButtonPress-3>", self.place_point)
        #self.root.bind("<B3-Motion>", self.place_point)
        self.grid.canvas.bind("<ButtonPress-3>", self.place_point)
        self.grid.canvas.bind("<B3-Motion>", self.place_point)
        # Mousewheel zooms too.
        # <MouseWheel> works on Windows/macOS.
        # <Button-4>/<Button-5> work on many Linux Tk builds.
        #self.root.bind("<MouseWheel>", self.mousewheel_zoom)
        #self.root.bind("<Button-4>", self.mousewheel_zoom)
        #self.root.bind("<Button-5>", self.mousewheel_zoom)

        self.grid.canvas.bind("<MouseWheel>", self.mousewheel_zoom)
        self.grid.canvas.bind("<Button-4>", self.mousewheel_zoom)
        self.grid.canvas.bind("<Button-5>", self.mousewheel_zoom)


        self.root.bind("<Control-z>", self.undo_prev_vertex)

        self.root.config(cursor="none")
        
        self.root.update()
        self.root.update_idletasks()
        
        
        #self.root.mainloop()

    def undo_prev_vertex(self, event):
        print("undo")
        try:
            self.polygons[self.selected_polygon].points.pop()
            
        except (IndexError):
            return

        #self.polygons[self.selected_polygon].redraw()
        self.grid.redraw(event=None)

    def select_polygon(self, event):
        # Number keys 1-9 select polygon indexes 0-8.
        # This avoids selecting index 9 when only 9 polygons exist.
        if (event.char not in [str(i) for i in range(1, len(self.polygons) + 1)]):
            return

        elif (event.char in [str(i) for i in range(1, len(self.polygons) + 1)]):
            self.selected_polygon = int(event.char) - 1
            print(f"selected polygon {self.selected_polygon + 1}")
            self.grid.redraw(event=None)

    def winfo_width(self):
        return self.root.winfo_width()

    def winfo_height(self):
        return self.root.winfo_height()

    def winfo_x(self):
        return self.root.winfo_x()
    
    def winfo_y(self):
        return self.root.winfo_y()

    def end_program(self, event):
        self.root.destroy()

    def redraw(self):
        # Draw every polygon, not only the selected one.
        # That is what makes polygons stay disjoint/independent on screen.
        for index, poly in enumerate(self.polygons):
            poly.redraw()

            for point in poly.points:
                x = self.grid.offset_x + (point.col * self.grid.space_x)
                y = self.grid.offset_y + (point.row * self.grid.space_y)
                point.x = x
                point.y = y

                # Only show vertices for the selected polygon.
                # Non-selected polygons stay visible, but their blue handles are hidden.
                if self.show_vertices and index == self.selected_polygon:
                    self.draw_circle((x, y), 5, "blue", point.tag)
                else:
                    self.grid.canvas.delete(point.tag)

    def toggle_vertices(self, event=None):
        self.show_vertices = not self.show_vertices
        self.grid.redraw(event=None)

    def draw_circle(self, center, radius, color, tag):
        self.grid.canvas.delete(tag)
        cx, cy = center
        self.grid.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, 
                                     fill=color, tags=(tag,))


    def place_point(self, event):
        print(f"selected polygon {self.selected_polygon + 1}")
        column, row = self.clamp_point((event.x, event.y))
        point = Point(
            self.grid.offset_x + (column * self.grid.space_x),
            self.grid.offset_y + (row * self.grid.space_y),
            f"point - {len(self.polygons[self.selected_polygon].points) + 1} - {self.selected_polygon}"
        )
        point.col = column
        point.row = row
        #self.graph_points.append(point)
        self.polygons[self.selected_polygon][len(self.polygons[self.selected_polygon].points)] = point
        self.polygons[self.selected_polygon].anchor_point(point)
        if self.show_vertices:
            self.draw_circle(point, 5, "blue", point.tag)
        self.grid.redraw(event=None)

    def clamp_point(self, point):
        column = nint((point[0] - self.grid.offset_x) / self.grid.space_x)
        row = nint((point[1] - self.grid.offset_y) / self.grid.space_y)
        return (column, row)

    def start_pan(self, event):
        self.root.config(cursor="fleur")
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.pan_origin_x = self.grid.offset_x
        self.pan_origin_y = self.grid.offset_y

    def pan(self, event):
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y

        self.grid.offset_x = self.pan_origin_x + dx
        self.grid.offset_y = self.pan_origin_y + dy

        self.grid.redraw(event=None)

    def end_pan(self, event):
        self.root.config(cursor="none")

    def mousewheel_zoom(self, event):
        direction = 0

        # Windows/macOS usually send <MouseWheel> with event.delta.
        if (hasattr(event, "delta") and event.delta != 0):
            if (event.delta > 0):
                direction = 1
            else:
                direction = -1

        # Linux often sends mouse wheel as Button-4 / Button-5.
        elif (hasattr(event, "num")):
            if (event.num == 4):
                direction = 1
            elif (event.num == 5):
                direction = -1

        if (direction == 0):
            return

        self.grid.apply_zoom(direction, anchor_x=event.x, anchor_y=event.y)

    def clamp_cursor(self, event):
        #mouse_pos = (event.x, event.y)
        #column = nint(event.x/self.grid.space_x)
        #row = nint(event.y/self.grid.space_y)
        column, row = self.clamp_point((event.x, event.y))
        x = self.grid.offset_x + (column * self.grid.space_x)
        y = self.grid.offset_y + (row * self.grid.space_y)
        self.draw_circle((x, y), 5, "green", "cursor")
