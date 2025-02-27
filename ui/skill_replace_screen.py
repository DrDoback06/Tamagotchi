# ui/skill_replace_screen.py

import pygame

class SkillReplaceScreen:
    def __init__(self, screen, creature, pending_skill, on_selection):
        """
        :param screen: pygame display surface.
        :param creature: The Creature object.
        :param pending_skill: The new candidate Ability object.
        :param on_selection: Callback that takes one argument (the index of the ability to replace)
                             or None if the player cancels.
        """
        self.screen = screen
        self.creature = creature
        self.pending_skill = pending_skill
        self.on_selection = on_selection
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        # Determine eligible abilities (index in creature.abilities) with tier <= pending_skill.tier
        self.eligible_indices = [i for i, ability in enumerate(creature.abilities) if ability.tier <= pending_skill.tier]
        if not self.eligible_indices:
            self.message = "No current ability eligible for replacement."
        else:
            self.message = f"Select an ability to replace with {str(pending_skill)}:"
        # Create button rects for each eligible ability
        self.buttons = []
        y = 150
        for i in self.eligible_indices:
            rect = pygame.Rect(100, y, 600, 50)
            self.buttons.append((i, rect))
            y += 60
        # Cancel button
        self.cancel_button = pygame.Rect(350, y, 150, 50)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for idx, rect in self.buttons:
                    if rect.collidepoint(pos):
                        self.on_selection(idx)
                if self.cancel_button.collidepoint(pos):
                    self.on_selection(None)

    def update(self, dt):
        pass

    def draw(self):
        # Draw a semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        # Title
        title = self.title_font.render("Skill Replacement", True, (255, 255, 255))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 50))
        # Draw the message
        lines = self.message.split('\n')
        y = 120
        for line in lines:
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (100, y))
            y += 40
        # Draw eligible ability buttons
        for idx, rect in self.buttons:
            pygame.draw.rect(self.screen, (100, 100, 100), rect)
            ability = self.creature.abilities[idx]
            text = self.font.render(f"Replace: {str(ability)}", True, (255, 255, 255))
            self.screen.blit(text, (rect.x + 10, rect.y + 10))
        # Draw Cancel button
        pygame.draw.rect(self.screen, (200, 0, 0), self.cancel_button)
        cancel_text = self.font.render("Cancel", True, (255, 255, 255))
        self.screen.blit(cancel_text, (self.cancel_button.x + 10, self.cancel_button.y + 10))
