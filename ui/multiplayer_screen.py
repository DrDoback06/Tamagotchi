# ui/multiplayer_screen.py

import pygame
import json
from battle_system import Battle
from abilities import ability_from_dict
from ui.levelup_screen import LevelUpScreen
from ui.skill_replace_screen import SkillReplaceScreen

class MultiplayerScreen:
    def __init__(self, screen, battle_start_data, network_client, on_main_menu=None, on_battle_complete=None):
        """
        :param battle_start_data: dict from server's BATTLE_START message.
        :param on_battle_complete: callback (no arguments) called after battle and popups finish.
        """
        self.screen = screen
        self.network = network_client
        self.on_main_menu = on_main_menu
        self.on_battle_complete = on_battle_complete
        self.font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 36)
        self.awarded_xp = False
        self.levelup_screen = None
        self.ready_to_exit = False
        self.action_log = []

        self.my_role = battle_start_data.get("your_role", "player1")
        self.current_turn = battle_start_data.get("current_turn", "player1")
        self.opponent_role = "player2" if self.my_role == "player1" else "player1"

        print(f"[Debug] MultiplayerScreen init: my_role={self.my_role}, current_turn={self.current_turn}, opponent_role={self.opponent_role}")

        player_creature_data = battle_start_data["player_creature"]
        opponent_creature_data = battle_start_data["opponent_creature"]
        self.player_creature = self.reconstruct_creature(player_creature_data)
        self.opponent_creature = self.reconstruct_creature(opponent_creature_data)
        print(f"[Debug] Player creature: {self.player_creature}")
        print(f"[Debug] Opponent creature: {self.opponent_creature}")

        self.battle = Battle(self.player_creature, self.opponent_creature)
        self.message = f"Battle begins! Turn: {self.current_turn}"
        self.action_log.append(self.message)
        print(f"[Debug] {self.message}")

        self.menu_button = pygame.Rect(650, 20, 120, 40)

    def reconstruct_creature(self, creature_data):
        from creatures import Creature
        c = Creature(chosen_type=creature_data["creature_type"])
        c.max_hp = creature_data["max_hp"]
        c.attack = creature_data["attack"]
        c.defense = creature_data["defense"]
        c.speed = creature_data["speed"]
        c.current_hp = creature_data["current_hp"]
        c.level = creature_data["level"]
        c.xp = creature_data["xp"]
        c.evolution_stage = creature_data["evolution_stage"]
        c.age = creature_data["age"]
        c.is_alive = creature_data["is_alive"]
        c.hunger = creature_data.get("hunger", 0)
        c.energy = creature_data.get("energy", 100)
        c.abilities = [ability_from_dict(a_dict) for a_dict in creature_data["abilities"]]
        return c

    def handle_events(self, events):
        if self.levelup_screen is not None:
            self.levelup_screen.handle_events(events)
            return
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.battle.battle_over and self.on_main_menu:
                        print("[Debug] ESC pressed and battle over. Returning to main menu.")
                        self.network.close()
                        self.on_main_menu()
                    else:
                        print("[Debug] ESC pressed but battle in progress; ignoring.")
                elif event.key == pygame.K_RETURN:
                    if self.battle.battle_over and self.ready_to_exit:
                        print("[Debug] ENTER pressed; exiting battle and saving creature stats.")
                        if self.on_battle_complete:
                            self.on_battle_complete()
                else:
                    if not self.battle.battle_over and self.current_turn == self.my_role:
                        if event.key in [pygame.K_1, pygame.K_KP1]:
                            self.send_move(0)
                        elif event.key in [pygame.K_2, pygame.K_KP2]:
                            self.send_move(1)
                        elif event.key in [pygame.K_3, pygame.K_KP3]:
                            self.send_move(2)
                        elif event.key in [pygame.K_4, pygame.K_KP4]:
                            self.send_move(3)
                    else:
                        print("[Debug] Not my turn or battle over; key press ignored.")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.menu_button.collidepoint(mouse_pos):
                    if self.battle.battle_over and self.on_main_menu:
                        print("[Debug] Main Menu button clicked and battle over. Returning to main menu.")
                        self.network.close()
                        self.on_main_menu()
                    else:
                        print("[Debug] Main Menu button clicked but battle in progress; ignoring.")

    def send_move(self, ability_index):
        print(f"[Debug] {self.my_role} is sending MOVE with ability index {ability_index}")
        self.battle.apply_attack(self.player_creature, self.opponent_creature, ability_index)
        self.message = self.battle.message
        self.action_log.append(self.message)
        print(f"[Debug] After local attack: {self.message}")
        next_turn = self.opponent_role
        print(f"[Debug] Switching turn. Next turn will be {next_turn}")
        move_msg = {
            "type": "MOVE",
            "index": ability_index,
            "next_turn": next_turn,
            "sender_role": self.my_role
        }
        self.network.send(json.dumps(move_msg))
        print(f"[Debug] Sent MOVE message: {json.dumps(move_msg)}")
        self.current_turn = next_turn
        print(f"[Debug] Local current_turn updated to {self.current_turn}")

    def update(self, dt):
        if self.levelup_screen is not None:
            self.levelup_screen.update(dt)
            return

        incoming = self.network.get_message()
        if incoming:
            print(f"[Debug] Received message: {incoming}")
            try:
                msg = json.loads(incoming)
                if msg.get("type") == "MOVE":
                    if msg.get("sender_role") == self.my_role:
                        print("[Debug] Ignoring our own echoed MOVE message.")
                    else:
                        index = msg["index"]
                        next_turn = msg["next_turn"]
                        print(f"[Debug] Processing MOVE from opponent: index={index}, next_turn={next_turn}")
                        self.battle.apply_attack(self.opponent_creature, self.player_creature, index)
                        self.action_log.append(self.battle.message)
                        self.current_turn = next_turn
                        self.message = self.battle.message
                        print(f"[Debug] Updated current_turn: {self.current_turn}, message: {self.message}")
            except Exception as e:
                print("[Debug] Error processing incoming message:", e)

        if self.battle.battle_over and not self.ready_to_exit:
            self.ready_to_exit = True
            if self.battle.winner == "player":
                prev_level = self.player_creature.level
                self.player_creature.gain_xp(100)
                if self.player_creature.level > prev_level and self.player_creature.pending_skill:
                    print("[Debug] Level up detected. Launching LevelUpScreen popup.")
                    xp_gained = 100
                    self.levelup_screen = LevelUpScreen(
                        self.screen,
                        self.player_creature,
                        self.player_creature.pending_skill,
                        xp_gained,
                        self.levelup_decision_callback
                    )
                else:
                    self.message = "You won! Gained 100 XP. Press ENTER to continue."
            else:
                self.player_creature.lose_xp(50)
                self.message = "You lost! Lost 50 XP. Press ENTER to continue."
            print(f"[Debug] Battle over. Winner: {self.battle.winner}")

    def levelup_decision_callback(self, decision):
        if decision:
            print("[Debug] Player chose to apply the new skill. Launching SkillReplaceScreen popup.")
            self.levelup_screen = SkillReplaceScreen(
                self.screen,
                self.player_creature,
                self.player_creature.pending_skill,
                self.skill_replace_callback
            )
        else:
            print("[Debug] Player chose to discard the new skill.")
            self.player_creature.pending_skill = None
            self.player_creature.level_just_upgraded = False
            self.levelup_screen = None

    def skill_replace_callback(self, index):
        if index is not None:
            print(f"[Debug] Replacing ability at index {index} with new skill.")
            self.player_creature.abilities[index] = self.player_creature.pending_skill
        else:
            print("[Debug] Player canceled ability replacement.")
        self.player_creature.pending_skill = None
        self.player_creature.level_just_upgraded = False
        self.levelup_screen = None

    def draw(self):
        self.screen.fill((0, 0, 50))
        title_text = self.title_font.render("Multiplayer Battle", True, (255, 255, 255))
        self.screen.blit(title_text, (300, 10))

        pygame.draw.rect(self.screen, (150, 0, 150), self.menu_button)
        menu_text = self.font.render("Main Menu", True, (255, 255, 255))
        self.screen.blit(menu_text, (self.menu_button.x + 5, self.menu_button.y + 5))

        player_text = self.font.render(f"{self.my_role}: {self.player_creature.creature_type}", True, (255, 255, 255))
        self.screen.blit(player_text, (50, 50))
        player_hp = self.font.render(f"HP: {self.player_creature.current_hp}/{self.player_creature.max_hp}", True, (255, 255, 255))
        self.screen.blit(player_hp, (50, 80))
        energy_text = self.font.render(f"Energy: {self.player_creature.energy}", True, (255, 255, 255))
        self.screen.blit(energy_text, (50, 110))

        opp_text = self.font.render(f"{self.opponent_role}: {self.opponent_creature.creature_type}", True, (255, 255, 255))
        self.screen.blit(opp_text, (450, 50))
        opp_hp = self.font.render(f"HP: {self.opponent_creature.current_hp}/{self.opponent_creature.max_hp}", True, (255, 255, 255))
        self.screen.blit(opp_hp, (450, 80))

        # Draw action log (last 4 actions)
        log_y = 150
        for action in self.action_log[-4:]:
            log_text = self.font.render(action, True, (200, 200, 0))
            self.screen.blit(log_text, (50, log_y))
            log_y += 30

        if not self.battle.battle_over:
            if self.current_turn == self.my_role:
                instructions = "Your Turn! Choose an Ability (1-4):"
                turn_text = self.font.render(instructions, True, (255, 255, 255))
                self.screen.blit(turn_text, (50, 500))
                for i, ability in enumerate(self.player_creature.abilities):
                    ability_str = str(ability)
                    ability_text = self.font.render(f"{i+1}: {ability_str}", True, (200, 200, 200))
                    self.screen.blit(ability_text, (50, 530 + i * 30))
            else:
                waiting_text = "Waiting for Opponent..."
                wait_surf = self.font.render(waiting_text, True, (255, 255, 255))
                self.screen.blit(wait_surf, (50, 500))
        else:
            end_prompt = "Battle over. Press ENTER to return to Creature Screen."
            prompt_text = self.font.render(end_prompt, True, (255, 255, 0))
            self.screen.blit(prompt_text, (200, 300))

        if self.levelup_screen is not None:
            self.levelup_screen.draw()
