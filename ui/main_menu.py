# ui/main_menu.py

import pygame
import os
import json

class MainMenu:
    def __init__(self, screen, on_new_game, on_creature_selector):
        self.screen = screen
        self.on_new_game = on_new_game
        self.on_creature_selector = on_creature_selector
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.new_game_button = pygame.Rect(100, 200, 200, 50)
        self.creature_selector_button = pygame.Rect(100, 280, 200, 50)
        self.graveyard_button = pygame.Rect(100, 360, 200, 50)
        self.graveyard_screen = None  # Will hold an instance of GraveyardScreen

    def tombstones_exist(self):
        if os.path.exists("tombstones.json"):
            try:
                with open("tombstones.json", "r") as f:
                    data = json.load(f)
                return len(data) > 0
            except:
                return False
        return False

    def handle_events(self, events, current_creature=None):
        # If the Graveyard screen is open, delegate events to it first.
        if self.graveyard_screen:
            self.graveyard_screen.handle_events(events)
            return

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.new_game_button.collidepoint(pos):
                    self.on_new_game()
                elif self.creature_selector_button.collidepoint(pos):
                    self.on_creature_selector()
                elif self.graveyard_button.collidepoint(pos):
                    if self.tombstones_exist():
                        from ui.graveyard_screen import GraveyardScreen
                        # Create GraveyardScreen with a callback to close
                        self.graveyard_screen = GraveyardScreen(self.screen, on_close=self.close_graveyard)
                    else:
                        print("[MainMenu] No tombstones found.")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESC in MainMenu might do nothing or quit the game
                    pass

    def close_graveyard(self):
        """Callback used by GraveyardScreen to close itself."""
        self.graveyard_screen = None

    def update(self, dt):
        if self.graveyard_screen:
            self.graveyard_screen.update(dt)

    def draw(self, current_creature=None):
        self.screen.fill((20, 20, 60))
        title_surf = self.title_font.render("Main Menu", True, (255, 255, 255))
        self.screen.blit(title_surf, (100, 100))

        pygame.draw.rect(self.screen, (0, 200, 0), self.new_game_button)
        new_game_text = self.font.render("New Game", True, (0, 0, 0))
        self.screen.blit(new_game_text, (self.new_game_button.x + 10, self.new_game_button.y + 10))

        pygame.draw.rect(self.screen, (0, 200, 200), self.creature_selector_button)
        selector_text = self.font.render("Select Creature", True, (0, 0, 0))
        self.screen.blit(selector_text, (self.creature_selector_button.x + 10, self.creature_selector_button.y + 10))

        # Graveyard button
        if self.tombstones_exist():
            pygame.draw.rect(self.screen, (150, 0, 150), self.graveyard_button)
            grave_text = self.font.render("Graveyard", True, (255, 255, 255))
        else:
            pygame.draw.rect(self.screen, (80, 80, 80), self.graveyard_button)
            grave_text = self.font.render("Graveyard", True, (50, 50, 50))
        self.screen.blit(grave_text, (self.graveyard_button.x + 10, self.graveyard_button.y + 10))

        # Show current creature summary if any
        if current_creature:
            # Draw a panel or text
            pass

        # If Graveyard screen is open, draw it on top
        if self.graveyard_screen:
            self.graveyard_screen.draw()
