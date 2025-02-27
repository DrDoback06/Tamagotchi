# ui/multiplayer_lobby_screen.py

import pygame
import json

class MultiplayerLobbyScreen:
    def __init__(self, screen, player_creature, network_client, on_start_battle, on_main_menu=None):
        """
        :param on_start_battle: function that takes one argument (the full BATTLE_START dict)
        """
        self.screen = screen
        self.player_creature = player_creature
        self.network = network_client
        self.on_start_battle = on_start_battle
        self.on_main_menu = on_main_menu
        self.font = pygame.font.Font(None, 36)
        self.message = "Press ENTER to join the lobby, ESC for Main Menu."
        self.menu_button = pygame.Rect(650, 20, 120, 40)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.on_main_menu()
                elif event.key == pygame.K_RETURN:
                    creature_data = self.player_creature.to_dict()
                    msg = {
                        "type": "JOIN_LOBBY",
                        "creature": creature_data
                    }
                    self.network.send(json.dumps(msg))
                    self.message = "Joined lobby... waiting for a match."
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.menu_button.collidepoint(mouse_pos):
                    self.on_main_menu()

    def update(self, dt):
        incoming = self.network.get_message()
        if incoming:
            try:
                msg_obj = json.loads(incoming)
                if msg_obj["type"] == "BATTLE_START":
                    self.on_start_battle(msg_obj)
            except Exception as e:
                print("[Lobby] Error parsing message:", e)

    def draw(self):
        self.screen.fill((20, 20, 60))
        text_surf = self.font.render("Multiplayer Lobby", True, (255, 255, 255))
        self.screen.blit(text_surf, (250, 50))
        msg_surf = self.font.render(self.message, True, (200, 200, 0))
        self.screen.blit(msg_surf, (100, 200))
        pygame.draw.rect(self.screen, (150, 0, 150), self.menu_button)
        menu_text = self.font.render("Main Menu", True, (255, 255, 255))
        self.screen.blit(menu_text, (self.menu_button.x + 5, self.menu_button.y + 5))
