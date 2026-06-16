#from tkinter import Canvas
from basic_geometry import *
import math
nint = lambda x: (math.floor(x + 0.5) + math.ceil((2*x - 1)/4) - math.floor((2*x - 1)/4) - 1) # nearest integer function

def draw_rectangle(**kw):
    canvas = kw["canvas"]
    args = kw["args"]
    tag = kw["tag"]
    mouse_pos = kw["mouse_pos"]
    canvas.create_rectangle(args["geometry"]["topleft"] + mouse_pos,
                            fill=args["style"]["color"], outline=args["style"]["outline"], 
                            tags=(tag,))

def draw_oval(**kw):
    canvas = kw["canvas"]
    args = kw["args"]
    tag = kw["tag"]
    mouse_pos = kw["mouse_pos"]
    canvas.create_oval(args["geometry"]["center"] + mouse_pos,
                            fill=args["style"]["color"], outline=args["style"]["outline"], 
                            tags=(tag,))

def draw_circle(**kw):
    canvas = kw["canvas"]
    args = kw["args"]
    tag = kw["tag"]
    mouse_pos = kw["mouse_pos"]
    cx, cy = args["geometry"]["center"]
    x, y = mouse_pos
    dx = cx - x
    dy = cy - y
    radius = nint(math.dist((cx, cy), (x, y)))
    custom_circle_args = (cx - radius, cy - radius,cx + radius,cy + radius)
    canvas.create_oval(custom_circle_args,fill=args["style"]["color"], outline=args["style"]["outline"], tags=(tag,))


def draw_shape_on_canvas(**kw):#canvas, args, tag

    shape_type = kw["shape_type"]
    if (shape_type == "rectangle"):
        draw_rectangle(**kw)
    elif (shape_type == "oval"):
        draw_oval(**kw)
    elif (shape_type == "circle"):
        draw_circle(**kw)

