# main.py
import pygame
from game_engine import GameEngine

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Dark Tamagotchi")
    clock = pygame.time.Clock()
    engine = GameEngine(screen)

    running = True
    while running:
        dt = clock.tick(60)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        engine.handle_events(events)
        engine.update(dt)
        engine.draw()
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
