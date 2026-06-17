from tkinter import Canvas
import math
import re


RECTANGLE_TYPE      = 0x00001
CIRCLE_TYPE         = 0x00002
OVAL_TYPE           = 0x00004
HIGHDEF_CIRCLE_TYPE = 0x00008
LINE_TYPE           = 0x00016
POINT_TYPE          = 0x00032
TRIANGLE_TYPE       = 0x00064
RHOMBUS_TYPE        = 0x00128

type_map = {
                "rectangle" : RECTANGLE_TYPE,
                "circle" : CIRCLE_TYPE,
                "oval" : OVAL_TYPE,
                "highdef circle" : HIGHDEF_CIRCLE_TYPE,
                "line" : LINE_TYPE,
                "point" : POINT_TYPE,
                "triangle" : TRIANGLE_TYPE,
                "rhombus" : RHOMBUS_TYPE
            }


nint = lambda x: (math.floor(x + 0.5) + math.ceil((2*x - 1)/4) - math.floor((2*x - 1)/4) - 1) # nearest integer function


class Shape:

    geom_keys = ()
    style_keys = ("color", "outline", "filled", "transparency")

    def __init__(self, kw):
        for key in (list(self.geom_keys) + list(self.style_keys)):
            setattr(self, key, kw[key])

        self.geom_attributes = list(type(self).geom_keys)
        self.style_attributes = list(type(self).style_keys)
        self.type = type(self).__name__.lower()
        self.z_index = None
        self.grabbed = False
        self.dx = None
        self.dy = None
        self.tag = None

    def collidepoint(self, point):
        pass

    def draw(self, canvas):
        pass

    def get_a_string(self, keys_):
        string = f"{getattr(self, keys_[0])}"
        for i in range(1, len(keys_)):
            string += f", {getattr(self, keys_[i])}"
        return string

    def __str__(self):
        key_string = self.get_a_string(self.geom_attributes)
        value_string = self.get_a_string(self.style_attributes)
        string = key_string + " : " + value_string
        return string

class Rectangle (Shape):
    geom_keys = ("topleft", "end")
    
    def __init__(self, kw):
        super().__init__(kw)
        self.geom_attributes += ["width", "height"]
        self.width = abs(self.topleft[0] - self.end[0])
        self.height = abs(self.topleft[1] - self.end[1])

    def collidepoint(self, point):
        print(self)
        x, y = point
        if (((self.end[0] >= x) and (self.topleft[0] <=x)) and ((self.end[1] >= y) and (self.topleft[1] <= y))):
            return True
        return False

    def draw(self, canvas):
        canvas.create_rectangle(self.topleft + self.end, fill=self.color, outline=self.outline, tags=(self.tag,))

class Circle (Shape):
    geom_keys = ("center", "end")

    def __init__(self, kw):
        super().__init__(kw)
        self.geom_attributes += ["radius"]
        self.radius = nint(math.dist(self.center, self.end))

    def collidepoint(self, point):
        if nint(math.dist(self.center, point)) <= self.radius:
            return True
        return False
    
    def draw(self, canvas):
        cx, cy = self.center
        radius = self.radius
        custom_circle_args = (cx - radius, cy - radius,cx + radius,cy + radius)
        canvas.create_oval(custom_circle_args,fill=self.color, outline=self.outline, tags=(self.tag,))

class Oval (Shape):
    geom_keys = ("center", "end")
    def __init__(self, kw):
        super().__init__(kw)
        self.geom_attributes += ["radius", "width", "height"] # width, height for boundbox if drawing with pygame
        self.radius = nint(math.dist(self.center, self.end)/2)
        self.width = self.end[0] - (self.center[0])
        self.height = self.end[1] - (self.center[1])
        self.start = self.center
        self.center = (self.center[0] + nint(self.width/2), self.center[1] + nint(self.height/2))

    def collidepoint(self, point):
        x, y = point
        a = nint(self.width/2)
        b = nint(self.height/2)
        cx, cy = self.center

        if ((((cx - x)**2)/(a**2)) + (((cy - y)**2)/(b**2)) < 1) or (abs(((((cx - x)**2)/(a**2)) + (((cy - y)**2)/(b**2))) - 1) < 0.01):
            return True
        return False

    def draw(self, canvas):
        canvas.create_oval(self.start + self.end, fill=self.color, outline=self.outline, tags=(self.tag,))

class Line (Shape):
    geom_keys = ("topleft", "end")
    def __init__(self, kw):
        super().__init__(kw)

class Point (Shape):
    geom_keys = ("end")
    def __init__(self, kw):
        super().__init__(kw)

class Triangle (Shape):
    geom_keys = ("center", "width", "height")
    
class ShapeFactory:
    shapes_map = {
                    RECTANGLE_TYPE : Rectangle,
                    CIRCLE_TYPE : Circle,
                    OVAL_TYPE : Oval
                 }
    @staticmethod
    def create(kw, specification):
        for flag, shape_class_ in ShapeFactory.shapes_map.items():
            if specification & flag:
                output_shape = shape_class_(kw)
                return output_shape

        raise ValueError("No shape type specification given")

"""
USAGE
args = {
            "topleft":(0, 0),
            "width": 20,
            "height": 30,
            "center":(2, 10),
            "end":(30, 20),
            "color": "black",
            "outline":"blue",
            "filled":False,
            "transparency":.5
       }

shape = ShapeFactory.create(args, RECTANGLE_TYPE)
print(shape.type)
print(shape)
"""
