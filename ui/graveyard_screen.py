# ui/graveyard_screen.py

import pygame
import json
import os
from character_manager import CharacterManager

class GraveyardScreen:
    def __init__(self, screen, on_close):
        """
        :param screen: pygame display surface
        :param on_close: callback to close this screen
        """
        self.screen = screen
        self.on_close = on_close  # We'll call this to remove ourselves
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.tombstones = self.load_tombstones()
        self.creature_manager = CharacterManager()
        self.selected_tombstone = None
        self.selected_creature = None
        self.close_button = pygame.Rect(650, 20, 120, 40)
        self.state = 0  # 0=choose tombstone, 1=choose creature

    def load_tombstones(self):
        if os.path.exists("tombstones.json"):
            try:
                with open("tombstones.json", "r") as f:
                    return json.load(f)
            except Exception as e:
                print("[Graveyard] Error loading tombstones:", e)
                return []
        else:
            return []

    def save_tombstones(self):
        with open("tombstones.json", "w") as f:
            json.dump(self.tombstones, f, indent=4)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.close_button.collidepoint(pos):
                    self.close()
                else:
                    if self.state == 0:
                        self.handle_tombstone_click(pos)
                    elif self.state == 1:
                        self.handle_creature_click(pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == 1:
                        # Go back to tombstone list
                        self.state = 0
                        self.selected_tombstone = None
                        self.selected_creature = None
                    else:
                        self.close()

    def handle_tombstone_click(self, pos):
        row_height = 30
        start_y = 100
        for i, tomb in enumerate(self.tombstones):
            row_rect = pygame.Rect(50, start_y + i*row_height, 600, row_height)
            if row_rect.collidepoint(pos):
                self.selected_tombstone = i
                xp_transferred = tomb.get("xp_transferred", False)
                bonus_xp = tomb.get("bonus_xp", 0)
                if xp_transferred or bonus_xp <= 0:
                    print("[Graveyard] No XP to transfer from this tombstone.")
                else:
                    # Move to state=1 to pick a living creature
                    self.state = 1
                break

    def handle_creature_click(self, pos):
        living_creatures = [c for c in self.creature_manager.get_all_creatures() if c.is_alive]
        row_height = 30
        start_y = 100
        for i, creature in enumerate(living_creatures):
            row_rect = pygame.Rect(50, start_y + i*row_height, 600, row_height)
            if row_rect.collidepoint(pos):
                self.selected_creature = creature
                self.transfer_xp()
                break

    def transfer_xp(self):
        if self.selected_tombstone is None or self.selected_creature is None:
            return
        tomb = self.tombstones[self.selected_tombstone]
        xp_transferred = tomb.get("xp_transferred", False)
        bonus_xp = tomb.get("bonus_xp", 0)
        if xp_transferred or bonus_xp <= 0:
            print("[Graveyard] XP not available.")
            return
        print(f"[Graveyard] Transferring {bonus_xp} bonus XP to {self.selected_creature.creature_type}.")
        self.selected_creature.xp += bonus_xp
        tomb["xp_transferred"] = True
        self.save_tombstones()

        from config import XP_MULTIPLIER
        xp_threshold = self.selected_creature.level * XP_MULTIPLIER
        if self.selected_creature.xp >= xp_threshold:
            self.selected_creature.level_up()
        self.creature_manager.save_characters()

        # Return to tombstone list
        self.state = 0
        self.selected_tombstone = None
        self.selected_creature = None
        print("[Graveyard] XP transfer complete.")

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill((30, 0, 30))
        title_text = self.title_font.render("Graveyard", True, (255, 255, 255))
        self.screen.blit(title_text, (300, 20))

        pygame.draw.rect(self.screen, (200, 0, 0), self.close_button)
        close_text = self.font.render("Close", True, (255, 255, 255))
        self.screen.blit(close_text, (self.close_button.x + 10, self.close_button.y + 5))

        if self.state == 0:
            self.draw_tombstone_list()
        else:
            self.draw_creature_list()

    def draw_tombstone_list(self):
        y = 100
        row_height = 30
        for i, tomb in enumerate(self.tombstones):
            xp_transferred = tomb.get("xp_transferred", False)
            bonus_xp = tomb.get("bonus_xp", 0)
            text_str = f"{i+1}. {tomb['creature_type']} - Lvl:{tomb['level']} - Bonus XP: {bonus_xp} - Transferred? {xp_transferred}"
            row_surf = self.font.render(text_str, True, (255, 255, 255))
            self.screen.blit(row_surf, (50, y))
            y += row_height
        instr = "Click a tombstone to attempt XP transfer (if available). ESC/Close to exit."
        instr_text = self.font.render(instr, True, (255, 255, 0))
        self.screen.blit(instr_text, (50, y + 30))

    def draw_creature_list(self):
        living_creatures = [c for c in self.creature_manager.get_all_creatures() if c.is_alive]
        y = 100
        row_height = 30
        for i, creature in enumerate(living_creatures):
            text_str = f"{i+1}. {creature.creature_type} (Lvl:{creature.level})"
            row_surf = self.font.render(text_str, True, (255, 255, 255))
            self.screen.blit(row_surf, (50, y))
            y += row_height
        instr = "Click a creature to receive XP. ESC to go back."
        instr_text = self.font.render(instr, True, (255, 255, 0))
        self.screen.blit(instr_text, (50, y + 30))

    def close(self):
        """Call the on_close callback to remove this screen from MainMenu."""
        self.on_close()
