# ui/levelup_screen.py

import pygame

class LevelUpScreen:
    def __init__(self, screen, creature, pending_skill, xp_gained, on_decision):
        """
        :param on_decision: callback function that takes one boolean argument.
                            True means "apply new skill", False means "discard".
        """
        self.screen = screen
        self.creature = creature
        self.pending_skill = pending_skill
        self.xp_gained = xp_gained
        self.on_decision = on_decision
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        # Simple button rectangles
        self.apply_button = pygame.Rect(200, 400, 150, 50)
        self.discard_button = pygame.Rect(400, 400, 150, 50)
        self.message = f"{creature.creature_type} reached Level {creature.level} and gained {xp_gained} XP!\nNew Skill:\n{str(pending_skill)}\nApply this skill?"

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.apply_button.collidepoint(mouse_pos):
                    self.on_decision(True)
                elif self.discard_button.collidepoint(mouse_pos):
                    self.on_decision(False)

    def update(self, dt):
        pass

    def draw(self):
        # Draw a semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        # Draw title
        title_text = self.title_font.render("Level Up!", True, (255, 255, 255))
        self.screen.blit(title_text, (self.screen.get_width()//2 - title_text.get_width()//2, 50))
        # Draw message (split by newlines)
        lines = self.message.split('\n')
        y = 150
        for line in lines:
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (100, y))
            y += 40
        # Draw Apply button
        pygame.draw.rect(self.screen, (0, 200, 0), self.apply_button)
        apply_text = self.font.render("Apply", True, (0, 0, 0))
        self.screen.blit(apply_text, (self.apply_button.x + 20, self.apply_button.y + 10))
        # Draw Discard button
        pygame.draw.rect(self.screen, (200, 0, 0), self.discard_button)
        discard_text = self.font.render("Discard", True, (255, 255, 255))
        self.screen.blit(discard_text, (self.discard_button.x + 10, self.discard_button.y + 10))
