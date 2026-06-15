import math


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
