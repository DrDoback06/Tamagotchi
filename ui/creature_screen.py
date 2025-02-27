import pygame
import time
from config import XP_MULTIPLIER

class CreatureScreen:
    def __init__(self, screen, creature, on_battle, on_adventure, on_main_menu):
        self.screen = screen
        self.creature = creature
        self.on_battle = on_battle          # Callback to start battle.
        self.on_adventure = on_adventure    # Callback to start training/adventure.
        self.on_main_menu = on_main_menu
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        # Define buttons for actions.
        self.battle_button = pygame.Rect(50, 400, 150, 50)
        self.train_button = pygame.Rect(250, 400, 150, 50)
        self.sleep_button = pygame.Rect(450, 400, 150, 50)
        self.inventory_button = pygame.Rect(650, 400, 150, 50)
        self.rest_button = pygame.Rect(350, 400, 150, 50)  # For laying to rest if dead.
        # NEW: Main Menu button (always visible)
        self.main_menu_button = pygame.Rect(650, 20, 150, 50)
        self.inventory_screen = None

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                # Main Menu button always works.
                if self.main_menu_button.collidepoint(pos):
                    self.on_main_menu()
                    continue
                # If creature is dead, allow only "Lay to Rest" and Main Menu actions.
                if not self.creature.is_alive:
                    if self.rest_button.collidepoint(pos):
                        self.lay_to_rest()
                    elif self.inventory_button.collidepoint(pos):
                        from ui.inventory_screen import InventoryScreen
                        self.inventory_screen = InventoryScreen(self.screen, self.creature, self.close_inventory)
                    elif self.battle_button.collidepoint(pos):
                        self.on_main_menu()
                    continue
                # If creature is alive:
                if self.battle_button.collidepoint(pos):
                    self.on_battle()
                elif self.train_button.collidepoint(pos):
                    self.on_adventure()
                elif self.sleep_button.collidepoint(pos):
                    if self.creature.is_sleeping:
                        self.creature.wake_up()
                    else:
                        self.creature.sleep()
                elif self.inventory_button.collidepoint(pos):
                    from ui.inventory_screen import InventoryScreen
                    self.inventory_screen = InventoryScreen(self.screen, self.creature, self.close_inventory)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Allow ESC to return to main menu
                    self.on_main_menu()

        if self.inventory_screen:
            self.inventory_screen.handle_events(events)

    def lay_to_rest(self):
        try:
            import json, os
            tombstone_file = "tombstones.json"
            record = self.creature.to_dict()
            record["laid_to_rest"] = True
            record["rested_at"] = time.time()
            record["bonus_xp"] = int(self.creature.level * 20 + self.creature.age / 10)
            if os.path.exists(tombstone_file):
                with open(tombstone_file, "r") as f:
                    data = json.load(f)
            else:
                data = []
            data.append(record)
            with open(tombstone_file, "w") as f:
                json.dump(data, f, indent=4)
            print(f"[Rest] {self.creature.creature_type} laid to rest.")
            print(f"[Rest] Bonus XP ({record['bonus_xp']}) recorded for XP transfer.")
            self.on_main_menu()
        except Exception as e:
            print("[Rest] Error laying creature to rest:", e)

    def close_inventory(self):
        self.inventory_screen = None

    def update(self, dt):
        self.creature.update_needs(dt)
        self.creature.update_age(dt)
        self.creature.update_effects()
        if self.inventory_screen:
            self.inventory_screen.update(dt)

    def draw(self):
        self.screen.fill((30, 30, 60))
        title = self.title_font.render("Creature Screen", True, (255, 255, 255))
        self.screen.blit(title, (300, 20))
        # Draw Main Menu button
        pygame.draw.rect(self.screen, (100, 100, 255), self.main_menu_button)
        mm_text = self.font.render("Main Menu", True, (0, 0, 0))
        self.screen.blit(mm_text, (self.main_menu_button.x + 5, self.main_menu_button.y + 10))
        stats = [
            f"Type: {self.creature.creature_type}",
            f"Level: {self.creature.level} (XP: {self.creature.xp}/{self.creature.level * XP_MULTIPLIER})",
            f"HP: {int(self.creature.current_hp)}/{self.creature.max_hp}",
            f"Energy: {int(self.creature.energy)}",
            f"Hunger: {int(self.creature.hunger)}",
            f"Age: {int(self.creature.age)} sec",
            f"Wellness: {self.creature.wellness}%",
            f"Mood: {self.creature.mood}/100"
        ]
        y = 100
        for line in stats:
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (50, y))
            y += 40
        # Draw mood slider.
        slider_width = 300
        slider_height = 20
        slider_x = 50
        slider_y = y + 20
        pygame.draw.rect(self.screen, (100, 100, 100), (slider_x, slider_y, slider_width, slider_height))
        fill_width = int((self.creature.mood / 100.0) * slider_width)
        pygame.draw.rect(self.screen, (0, 200, 0), (slider_x, slider_y, fill_width, slider_height))
        mood_text = self.font.render("Mood", True, (255, 255, 255))
        self.screen.blit(mood_text, (slider_x + slider_width + 10, slider_y))
        # Display abilities.
        abilities_title = self.font.render("Abilities:", True, (200, 200, 0))
        self.screen.blit(abilities_title, (50, slider_y + 40))
        y2 = slider_y + 40
        for ability in self.creature.abilities:
            ability_text = self.font.render(str(ability), True, (255, 255, 255))
            self.screen.blit(ability_text, (300, y2))
            y2 += 30
        # Draw action buttons.
        if self.creature.is_alive:
            pygame.draw.rect(self.screen, (0, 200, 0), self.battle_button)
            battle_text = self.font.render("Battle", True, (0, 0, 0))
            self.screen.blit(battle_text, (self.battle_button.x + 10, self.battle_button.y + 10))
            pygame.draw.rect(self.screen, (0, 200, 200), self.train_button)
            train_text = self.font.render("Train", True, (0, 0, 0))
            self.screen.blit(train_text, (self.train_button.x + 10, self.train_button.y + 10))
            pygame.draw.rect(self.screen, (200, 200, 0), self.sleep_button)
            sleep_text = self.font.render("Sleep/Wake", True, (0, 0, 0))
            self.screen.blit(sleep_text, (self.sleep_button.x + 5, self.sleep_button.y + 10))
            pygame.draw.rect(self.screen, (200, 0, 200), self.inventory_button)
            inv_text = self.font.render("Inventory", True, (255, 255, 255))
            self.screen.blit(inv_text, (self.inventory_button.x + 5, self.inventory_button.y + 10))
        else:
            dead_text = self.font.render(f"{self.creature.creature_type} is dead.", True, (255, 0, 0))
            self.screen.blit(dead_text, (50, 400))
            pygame.draw.rect(self.screen, (0, 0, 200), self.rest_button)
            rest_text = self.font.render("Lay to Rest", True, (255, 255, 255))
            self.screen.blit(rest_text, (self.rest_button.x + 10, self.rest_button.y + 10))
            pygame.draw.rect(self.screen, (150, 0, 150), self.battle_button)
            menu_text = self.font.render("Main Menu", True, (255, 255, 255))
            self.screen.blit(menu_text, (self.battle_button.x + 10, self.battle_button.y + 10))
        if self.inventory_screen:
            self.inventory_screen.draw()
