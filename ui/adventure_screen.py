import pygame
import random
from ui.levelup_screen import LevelUpScreen

class AdventureScreen:
    def __init__(self, screen, creature, on_main_menu, on_wild_battle):
        self.screen = screen
        self.creature = creature
        self.on_main_menu = on_main_menu
        self.on_wild_battle = on_wild_battle
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.message = "Exploring..."
        self.pop_up = None
        self.encounter_timer = random.randint(5000, 10000)  # 5-10 sec

    def handle_events(self, events):
        if self.pop_up:
            self.pop_up.handle_events(events)
            return
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.on_main_menu()

    def update(self, dt):
        if self.pop_up:
            self.pop_up.update(dt)
            return
        self.encounter_timer -= dt
        if self.encounter_timer <= 0:
            event_type = random.choice(["xp", "item", "ability"])
            if event_type == "xp":
                xp_gain = random.randint(20, 50)
                self.creature.gain_xp(xp_gain)
                self.message = f"Gained {xp_gain} XP from training!"
            elif event_type == "item":
                item = {"name": "Health Potion", "quantity": 1, "effect": {"type": "heal", "amount": 20}}
                self.creature.add_item(item)
                self.message = "Found a Health Potion!"
            elif event_type == "ability":
                xp_gain = random.randint(20, 50)
                self.creature.gain_xp(xp_gain)
                self.pop_up = LevelUpScreen(self.screen, self.creature, self.creature.pending_skill, xp_gain, self.reward_decision_callback)
                self.message = f"Training reward: {xp_gain} XP and an ability reward!"
            self.encounter_timer = random.randint(5000, 10000)

    def reward_decision_callback(self, decision):
        if decision:
            # For simplicity, replace the first ability.
            if self.creature.pending_skill:
                self.creature.abilities[0] = self.creature.pending_skill
        self.creature.pending_skill = None
        self.pop_up = None

    def draw(self):
        self.screen.fill((0, 50, 0))
        title_text = self.title_font.render("Adventure Mode", True, (255, 255, 255))
        self.screen.blit(title_text, (300, 20))
        msg_text = self.font.render(self.message, True, (255, 255, 0))
        self.screen.blit(msg_text, (50, 100))
        if self.pop_up:
            self.pop_up.draw()
