import math
import pygame
from pygame import gfxdraw
from .utils import Point


def draw_dashed_line(window, data):
    color, start_pos, end_pos, width, dash_length = data.get('color', 'black'), data['start_position'], data['end_position'], data.get('width', 1), data.get('dash_length', 10)
    origin = Point(start_pos)
    target = Point(end_pos)
    displacement = target - origin
    length = len(displacement)
    slope = displacement/length
    for index in range(0, length//dash_length, 2):
        start = origin + (slope *    index    * dash_length)
        end   = origin + (slope * (index + 1) * dash_length)
        pygame.draw.line(window, color, start.get(), end.get(), width)

def rgb_to_hex(*colour):
    """Creates a hex string from rgb args
    Args:
        colour (*int): rgb values
    Returns:
        str: rgb hex string
    """
    return "#%02x%02x%02x" % colour 

def draw_circle(window, data):
    # TODO antialiasing?
    pygame.draw.circle(window, data.get('color', 'black'), data['position'], data['radius'], width=data.get('width', 0)) 
    #gfxdraw.aacircle(window, int(data['position'][0]), int(data['position'][1]), int(data['radius']), (0,0,0)) #data.get('color', 'black'))

    
def draw_simple_rect(window, data):
    pygame.draw.rect(window, data.get('color', 'black'), (*data['position'], *data['size']), width=data.get('width', 0)) 

def draw_line(window, data):
    pygame.draw.line(window, data.get('color', 'black'), data['start_position'], data['end_position'], data.get('width', 1))

def clear(window, data):
    window.fill(data['color'])

def draw_rectangle(window, data):
    rotation = data.get('rotation', 0)
    if rotation == 0:
        return draw_simple_rect(window, data)
    x, y = data['position']
    width, height = data['size']
    points = []
    # The distance from the center of the rectangle to
    # one of the corners is the same for each corner.
    radius = math.sqrt((height / 2)**2 + (width / 2)**2)
    # Get the angle to one of the corners with respect
    # to the x-axis.
    angle = math.atan2(height / 2, width / 2)
    # Transform that angle to reach each corner of the rectangle.
    angles = [angle, -angle + math.pi, angle + math.pi, -angle]
    # Convert rotation from degrees to radians.
    rot_radians = (math.pi / 180) * rotation
    # Calculate the coordinates of each point.
    for angle in angles:
        y_offset = -1 * radius * math.sin(angle + rot_radians)
        x_offset = radius * math.cos(angle + rot_radians)
        points.append((x + x_offset, y + y_offset))

    pygame.draw.polygon(window, data.get('color', 'black'), points, width=data.get('width', 0))