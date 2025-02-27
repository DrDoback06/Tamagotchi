# ui/creature_selector.py

import pygame

class CreatureSelectorScreen:
    def __init__(self, screen, creatures, on_select, on_main_menu, on_delete):
        """
        :param screen: The pygame display surface.
        :param creatures: The list of creatures (from the CharacterManager).
        :param on_select: Callback when a creature is selected (creature -> None).
        :param on_main_menu: Callback to return to main menu.
        :param on_delete: Callback to delete a creature (creature -> None).
        """
        self.screen = screen
        self.creatures = creatures
        self.on_select = on_select
        self.on_main_menu = on_main_menu
        self.on_delete = on_delete  # Typically something like gameEngine.delete_creature
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        # Buttons
        self.back_button = pygame.Rect(50, 20, 150, 40)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                # Check if back button is clicked
                if self.back_button.collidepoint(pos):
                    self.on_main_menu()
                    return
                # Each creature is listed as a row to click on
                row_height = 60
                start_y = 100
                for i, creature in enumerate(self.creatures):
                    # For each creature, we might have "Select" and "Delete" sub-buttons
                    # We'll do a simple approach: left half for "Select", right half for "Delete"
                    row_rect = pygame.Rect(50, start_y + i * row_height, 600, row_height)
                    select_area = pygame.Rect(row_rect.x, row_rect.y, row_rect.width // 2, row_rect.height)
                    delete_area = pygame.Rect(row_rect.x + row_rect.width // 2, row_rect.y, row_rect.width // 2, row_rect.height)

                    if select_area.collidepoint(pos):
                        # The user clicked "select" for this creature
                        self.on_select(creature)
                        return
                    elif delete_area.collidepoint(pos):
                        # The user clicked "delete" for this creature
                        self.on_delete(creature)
                        # After deleting from the manager, RELOAD local list:
                        from character_manager import CharacterManager
                        cm = CharacterManager()  # Or if you already have a manager, use it directly
                        self.creatures = cm.get_all_creatures()
                        return

    def update(self, dt):
        pass

    def draw(self):
        self.screen.fill((40, 40, 40))
        title_surf = self.title_font.render("Creature Selector", True, (255, 255, 255))
        self.screen.blit(title_surf, (50, 40))

        # Draw back button
        pygame.draw.rect(self.screen, (200, 0, 0), self.back_button)
        back_text = self.font.render("Main Menu", True, (255, 255, 255))
        self.screen.blit(back_text, (self.back_button.x + 5, self.back_button.y + 5))

        row_height = 60
        start_y = 100
        for i, creature in enumerate(self.creatures):
            row_rect = pygame.Rect(50, start_y + i * row_height, 600, row_height)
            pygame.draw.rect(self.screen, (80, 80, 120), row_rect)

            # Left half is for "Select"
            select_area = pygame.Rect(row_rect.x, row_rect.y, row_rect.width // 2, row_rect.height)
            pygame.draw.rect(self.screen, (0, 200, 0), select_area)
            select_text = self.font.render(f"Select {creature.creature_type}", True, (0, 0, 0))
            self.screen.blit(select_text, (select_area.x + 5, select_area.y + 10))

            # Right half is for "Delete"
            delete_area = pygame.Rect(row_rect.x + row_rect.width // 2, row_rect.y, row_rect.width // 2, row_rect.height)
            pygame.draw.rect(self.screen, (200, 0, 0), delete_area)
            delete_text = self.font.render(f"Delete {creature.creature_type}", True, (255, 255, 255))
            self.screen.blit(delete_text, (delete_area.x + 5, delete_area.y + 10))

            # Additional creature info
            info_text = self.font.render(f"Lvl:{creature.level} HP:{int(creature.current_hp)}/{creature.max_hp}", True, (255, 255, 255))
            self.screen.blit(info_text, (row_rect.x + 10, row_rect.y + row_rect.height // 2))
