import pygame
import pygame.gfxdraw

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Antialiased Circle Drawing Example")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)

def draw_antialiased_circle_to_surface(window, position, radius, color, thickness):
    SCALE = 3
    _radius = radius * SCALE
    size = (_radius + 1) * 2
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (_radius, _radius)
    pygame.gfxdraw.filled_circle(surface, center[0], center[1], _radius, pygame.Color(color))
    pygame.gfxdraw.filled_circle(surface, center[0], center[1], _radius - thickness * SCALE, pygame.Color(0,0,0,0))
    surface = pygame.transform.smoothscale(surface, (size/SCALE, size/SCALE)) # this does the anti-alising... its not ideal but it works... stupid pygame
    window.blit(surface, (position[0] - radius, position[1] - radius))

# Set up game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(white)

    # Draw an antialiased circle to a temporary surface
    circle_radius = 100
    circle_color = 'blue'
    circle_thickness = 10
    position = (width // 2, height // 2)

    pygame.draw.rect(screen, 'black', (width // 2 - 100, height // 2 - 50, 100, 100), width=0)

    temp_surface = draw_antialiased_circle_to_surface(screen, position, circle_radius, circle_color, circle_thickness)
    


    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
