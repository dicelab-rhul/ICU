import multiprocessing
import pygame


import pygame

from .window import new_window, get_window_info

def start(config):
    pygame_process = multiprocessing.Process(target=run, args=[config])
    pygame_process.start()
    return pygame_process

def run(config):
    window = new_window(config['window_position'], config['window_size'])
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Draw shapes
        window.fill((255, 255, 255))
        pygame.draw.circle(window, (255, 0, 0), (150, 200), 50)
        pygame.draw.rect(window, (0, 200, 0), (100, 300, 300, 200))
        pygame.draw.line(window, (0, 0, 100), (100, 100), (700, 500), 5)
        pygame.display.flip()
    pygame.quit()


