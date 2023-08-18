import pygame
import pygame.gfxdraw

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Antialiased Polygon Line Drawing Example")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)

def draw_antialiased_polygon_line(surface, start_pos, end_pos, color, width):
    direction = pygame.math.Vector2(end_pos) - pygame.math.Vector2(start_pos)
    perpendicular = pygame.math.Vector2(-direction.y, direction.x)
    perpendicular.normalize_ip()
    half_width = width / 2
    points = [
        start_pos + perpendicular * half_width,
        end_pos + perpendicular * half_width,
        end_pos - perpendicular * half_width,
        start_pos - perpendicular * half_width
    ]
    pygame.gfxdraw.aapolygon(surface, points, color)
    pygame.gfxdraw.filled_polygon(surface, points, color)

def draw_polygon_line(surface, start_pos, end_pos, color, width):
    direction = pygame.math.Vector2(end_pos) - pygame.math.Vector2(start_pos)
    perpendicular = pygame.math.Vector2(-direction.y, direction.x)
    perpendicular.normalize_ip()

    half_width = width / 2
    points = [
        start_pos + perpendicular * half_width,
        end_pos + perpendicular * half_width,
        end_pos - perpendicular * half_width,
        start_pos - perpendicular * half_width
    ]

    #pygame.gfxdraw.aapolygon(surface, points, color)
    pygame.gfxdraw.filled_polygon(surface, points, color)


# Set up game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(white)

    # Draw an antialiased line with a width of 5 using polygons
    start_point = (100, 100)
    end_point = (700, 500)
    line_color = black
    line_width = 5
    draw_antialiased_polygon_line(screen, start_point, end_point, line_color, line_width)
    draw_polygon_line(screen, (start_point[0], start_point[1] + 50), (end_point[0], end_point[1] + 50), line_color, line_width)


    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()