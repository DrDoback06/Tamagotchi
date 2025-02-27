import pygame
from battle_system import Battle

class BattleScreen:
    def __init__(self, screen, battle, on_main_menu=None):
        """
        :param battle: An instance of the Battle class.
        :param on_main_menu: Callback to return to Main Menu.
        """
        self.screen = screen
        self.battle = battle  # Contains battle.player and battle.enemy.
        self.on_main_menu = on_main_menu
        self.font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 36)
        self.action_log = []
        self.message = "Battle begins! It's your turn."
        self.action_log.append(self.message)
        self.menu_button = pygame.Rect(650, 20, 120, 40)

    def handle_events(self, events):
        if self.battle.battle_over:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.on_main_menu:
                            self.on_main_menu()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.menu_button.collidepoint(event.pos):
                        if self.on_main_menu:
                            self.on_main_menu()
            return

        if self.battle.turn == "player":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.player_attack(0)
                    elif event.key == pygame.K_2:
                        self.player_attack(1)
                    elif event.key == pygame.K_3:
                        self.player_attack(2)
                    elif event.key == pygame.K_4:
                        self.player_attack(3)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.menu_button.collidepoint(event.pos):
                        if self.on_main_menu:
                            self.on_main_menu()
        else:
            # It's enemy turn; no input expected.
            pass

    def player_attack(self, ability_index):
        self.battle.apply_attack(self.battle.player, self.battle.enemy, ability_index)
        self.action_log.append(self.battle.message)
        if self.battle.battle_over:
            return
        self.battle.turn = "enemy"
        self.battle.enemy_turn()
        self.action_log.append(self.battle.message)
        if self.battle.battle_over:
            return
        self.battle.turn = "player"

    def update(self, dt):
        if self.battle.battle_over and not hasattr(self, "xp_processed"):
            self.xp_processed = True
            if self.battle.winner == "player":
                xp_gain = 50
                self.battle.player.gain_xp(xp_gain)
                self.action_log.append(f"You won! Gained {xp_gain} XP.")
            else:
                xp_loss = 30
                self.battle.player.lose_xp(xp_loss)
                self.action_log.append(f"You lost! Lost {xp_loss} XP.")

    def draw(self):
        self.screen.fill((0, 0, 50))
        title_text = self.title_font.render("Battle Screen", True, (255, 255, 255))
        self.screen.blit(title_text, (300, 10))

        pygame.draw.rect(self.screen, (150, 0, 150), self.menu_button)
        menu_text = self.font.render("Main Menu", True, (255, 255, 255))
        self.screen.blit(menu_text, (self.menu_button.x + 5, self.menu_button.y + 5))

        player_text = self.font.render(
            f"Player: {self.battle.player.creature_type} (HP: {int(self.battle.player.current_hp)}/{self.battle.player.max_hp})",
            True, (255, 255, 255))
        self.screen.blit(player_text, (50, 50))

        enemy_text = self.font.render(
            f"Enemy: {self.battle.enemy.creature_type} (HP: {int(self.battle.enemy.current_hp)}/{self.battle.enemy.max_hp})",
            True, (255, 255, 255))
        self.screen.blit(enemy_text, (50, 80))

        if not self.battle.battle_over:
            if self.battle.turn == "player":
                instr = "Your Turn! Press 1-4 to choose an ability."
                instr_text = self.font.render(instr, True, (255, 255, 255))
                self.screen.blit(instr_text, (50, 120))
                y_abilities = 150
                for i, ability in enumerate(self.battle.player.abilities[:4]):
                    ab_text = self.font.render(f"{i+1}: {ability}", True, (200, 200, 200))
                    self.screen.blit(ab_text, (50, y_abilities))
                    y_abilities += 30
            else:
                wait_text = self.font.render("Enemy Turn...", True, (255, 255, 255))
                self.screen.blit(wait_text, (50, 120))
        else:
            end_text = self.font.render("Battle over. Press ENTER to exit.", True, (255, 255, 0))
            self.screen.blit(end_text, (200, 300))

        y_log = 400
        for msg in self.action_log[-4:]:
            log_text = self.font.render(msg, True, (255, 255, 0))
            self.screen.blit(log_text, (50, y_log))
            y_log += 30
