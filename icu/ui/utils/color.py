
def string_to_rgb(color_string):
    """Convert a string representation of a color to an (R, G, B) tuple."""
    # You can expand this dictionary for other colors.
    color_map = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        # ... add other colors as needed
    }
    
    return color_map.get(color_string)

def brightness(color, factor=0.7):
    """Return a darker shade of the given color."""
    r, g, b = color
    return (int(r * factor), int(g * factor), int(b * factor))
