import pygame

class InventoryScreen:
    def __init__(self, screen, creature, on_close):
        """
        :param screen: pygame display surface.
        :param creature: The Creature object (with an inventory attribute).
        :param on_close: Callback when the inventory screen should close.
        """
        self.screen = screen
        self.creature = creature
        self.on_close = on_close
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.max_slots = 10
        self.refresh_buttons()
        self.close_button = pygame.Rect(650, 20, 120, 40)

    def refresh_buttons(self):
        self.buttons = []
        y = 150
        for i, item in enumerate(self.creature.inventory):
            if i >= self.max_slots:
                break
            rect = pygame.Rect(100, y, 600, 50)
            self.buttons.append((i, rect, item))
            y += 60

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.close_button.collidepoint(pos):
                    self.on_close()
                else:
                    for idx, rect, item in self.buttons:
                        if rect.collidepoint(pos):
                            used = self.creature.use_item(item["name"])
                            if used:
                                print(f"[Inventory] Used {item['name']}.")
                            else:
                                print(f"[Inventory] Could not use {item['name']}.")
                            self.refresh_buttons()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.on_close()

    def update(self, dt):
        pass

    def draw(self):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        title = self.title_font.render("Inventory", True, (255, 255, 255))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 50))
        for idx, rect, item in self.buttons:
            pygame.draw.rect(self.screen, (100, 100, 100), rect)
            item_text = self.font.render(f"{item['name']} (x{item['quantity']})", True, (255, 255, 255))
            self.screen.blit(item_text, (rect.x + 10, rect.y + 10))
        pygame.draw.rect(self.screen, (200, 0, 0), self.close_button)
        close_text = self.font.render("Close", True, (255, 255, 255))
        self.screen.blit(close_text, (self.close_button.x+10, self.close_button.y+10))
