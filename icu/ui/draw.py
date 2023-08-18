import math
import pygame
from pygame import gfxdraw
from .utils import Point

from .constants import LINE_COLOR, LINE_WIDTH, LINE_DASH_LENGTH

def rgb_to_hex(*colour):
    """Creates a hex string from rgb args
    Args:
        colour (*int): rgb values
    Returns:
        str: rgb hex string
    """
    return "#%02x%02x%02x" % colour 


def draw_dashed_line(window, start_position, end_position, width=LINE_WIDTH, color=LINE_COLOR, dash_length=LINE_DASH_LENGTH):
    origin = Point(start_position)
    target = Point(end_position)
    displacement = target - origin
    length = len(displacement)
    slope = displacement/length
    for index in range(0, length//dash_length, 2):
        start = origin + (slope *    index    * dash_length)
        end   = origin + (slope * (index + 1) * dash_length)
        pygame.draw.line(window, color, start.get(), end.get(), width) # TODO anti aliasing...

def clear(window, color):
    window.fill(color)

def draw_line(window, start_position, end_position, color=LINE_COLOR, width=LINE_WIDTH, anti_alias=True):
    if anti_alias:
       _aa_draw_line(window, start_position, end_position, color=color, line_width=width)
    else:
        _draw_line(window, start_position, end_position, color=color, width=width)
        
def draw_rectangle(window, position, size, rotation=0, color=LINE_COLOR, line_width=1, fill=False, anti_alias=True):
    line_width = line_width if not fill else 0
    if rotation % 90 == 0:
        # TODO test this... (AI GENERATED)
        if rotation == 0:
            return _draw_simple_rectangle(window, position=position, size=size, color=color, line_width=line_width)
        elif rotation == 90:
            return _draw_simple_rectangle(window, position=(position[0] - size[1], position[1]), size=(size[1], size[0]), color=color, line_width=line_width)
        elif rotation == 180:
            return _draw_simple_rectangle(window, position=(position[0] - size[0], position[1] - size[1]), size=size, color=color, line_width=line_width)
        elif rotation == 270:
            return _draw_simple_rectangle(window, position=position, size=(size[1], size[0]), color=color, line_width=line_width)
    x, y = position
    line_width, height = size
    points = []
    radius = math.sqrt((height / 2)**2 + (line_width / 2)**2)
    angle = math.atan2(height / 2, line_width / 2)
    angles = [angle, -angle + math.pi, angle + math.pi, -angle]
    rot_radians = (math.pi / 180) * rotation
    for angle in angles:
        y_offset = -1 * radius * math.sin(angle + rot_radians)
        x_offset = radius * math.cos(angle + rot_radians)
        points.append((x + x_offset, y + y_offset))
    draw_polygon(window, points, color=color, line_width=line_width, anti_alias=anti_alias, fill=fill)

def draw_arrow(window, start_position, length, width=LINE_WIDTH, color=LINE_COLOR, angle=0, 
               head_length=None, head_only=False, fill_head=False, anti_alias=True):
    start_position = tuple(start_position)
    angle = math.radians(angle)
    head_length = head_length if head_length is not None else length / 2
    # Calculate arrow end point
    arrow_end = (
        start_position[0] + length * math.cos(angle),
        start_position[1] - length * math.sin(angle),
    )
    # Calculate arrowhead points
    arrowhead_left = (
        arrow_end[0] - head_length * math.cos(angle + math.radians(30)),
        arrow_end[1] + head_length * math.sin(angle + math.radians(30))
    )
    arrowhead_right = (
        arrow_end[0] - head_length * math.cos(angle - math.radians(30)),
        arrow_end[1] + head_length * math.sin(angle - math.radians(30))
    )
    if not head_only:
        #gfxdraw.line(window, *start_position, *arrow_end, )
        draw_line(window, start_position, arrow_end, color=color, width=width, anti_alias=anti_alias)
    if not fill_head:
        draw_line(window, arrow_end, arrowhead_left, width=width, color=color, anti_alias=anti_alias)
        draw_line(window, arrow_end, arrowhead_right,width=width, color=color, anti_alias=anti_alias)
    else:
        draw_polygon(window, (arrowhead_left, arrowhead_right, arrow_end), color=color, fill=True)
      
def draw_polygon(window, points, color=LINE_COLOR, line_width=1, fill=False, anti_alias=True):
    if anti_alias:
        return _aa_draw_polygon(window, points, color=color, line_width=line_width, fill=fill)
    else:
        return _draw_polygon(window, points, color=color, line_width=line_width, fill=fill)

def draw_circle(window, position, radius, color=LINE_COLOR, line_width=1, fill=False, anti_alias=True):
    if anti_alias:
        return _aa_draw_circle(window, position, radius, color=color, line_width=line_width, fill=fill)
    else:
        return _draw_circle(window, position, radius, color=color, line_width=line_width, fill=fill)

def _draw_circle(window, position, radius, color=LINE_COLOR, line_width=0, fill=False):
    line_width = line_width if not fill else 0
    pygame.draw.circle(window, color, position, radius, width=line_width)

def _aa_draw_circle(window, position, radius, color=LINE_COLOR, line_width=1, fill=False):
    # this is a pretty dirty way to do things, but I could find another way.. let me know if you know!
    SCALE = 3 # reasonable value for a good quality circle
    _radius = radius * SCALE
    size = (_radius + 1) * 2
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (_radius, _radius)
    pygame.gfxdraw.filled_circle(surface, center[0], center[1], _radius, pygame.Color(color))
    if not fill:
        pygame.gfxdraw.filled_circle(surface, center[0], center[1], _radius - line_width * SCALE, pygame.Color(0,0,0,0))
    surface = pygame.transform.smoothscale(surface, (size/SCALE, size/SCALE)) # this does the anti-alising... its not ideal but it works... stupid pygame
    window.blit(surface, (position[0] - radius, position[1] - radius))

def _draw_polygon(window, points, color=LINE_COLOR, line_width=1, fill=False):
    line_width = line_width if not fill else 0
    pygame.draw.polygon(window, color, points, width=line_width)

def _aa_draw_polygon(window, points, color=LINE_COLOR, line_width=1, fill=False):
    color = pygame.Color(color)
    if fill:
        pygame.gfxdraw.aapolygon(window, points, color)
        pygame.gfxdraw.filled_polygon(window, points, color)
    else:
        if line_width == 1:
            pygame.gfxdraw.aapolygon(window, points, color)
        else:
            for i in range(len(points) - 1):  # got to draw a bunch of _aa_lines
                _aa_draw_line(window, points[i], points[i + 1], color=color, line_width=line_width)

def _draw_simple_rectangle(window, position, size, color=LINE_COLOR, line_width=1, fill=False):
    line_width = line_width if not fill else 0
    pygame.draw.rect(window, color, (*position, *size), width=line_width)

def _aa_draw_line(window, start_position, end_position, color=LINE_COLOR, line_width=LINE_WIDTH):
    start_position = tuple(start_position)
    end_position = tuple(end_position)
    color = pygame.Color(color)
    direction = pygame.math.Vector2(end_position) - pygame.math.Vector2(start_position)
    perpendicular = pygame.math.Vector2(-direction.y, direction.x)
    perpendicular.normalize_ip()
    half_width = (line_width-1) / 2
    points = [
        start_position + perpendicular * half_width,
        end_position + perpendicular * half_width,
        end_position - perpendicular * half_width,
        start_position - perpendicular * half_width
    ]
    pygame.gfxdraw.aapolygon(window, points, color)
    pygame.gfxdraw.filled_polygon(window, points, color)

def _draw_line(window, start_position, end_position, color=LINE_COLOR, width=LINE_WIDTH):
    pygame.draw.line(window, color, tuple(start_position), tuple(end_position), width=width)
