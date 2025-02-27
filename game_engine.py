import pygame
from ui.main_menu import MainMenu
from ui.creature_screen import CreatureScreen
from creatures import Creature
from ui.creature_selector import CreatureSelectorScreen
from character_manager import CharacterManager

class GameEngine:
    def __init__(self, screen):
        self.screen = screen
        self.state = "MAIN_MENU"
        self.current_creature = None  # Persistent creature instance.
        self.char_manager = CharacterManager()  # Responsible for saving/loading creatures.
        self.main_menu = MainMenu(
            screen,
            on_new_game=self.start_new_game,
            on_creature_selector=self.start_creature_selector
        )
        self.creature_screen = None
        self.battle_screen = None
        self.adventure_screen = None
        self.lobby_screen = None
        self.multiplayer_screen = None
        self.selector_screen = None
        self.autosave_timer = 0

    def start_new_game(self):
        if not self.current_creature:
            self.current_creature = Creature()
            self.char_manager.add_creature(self.current_creature)
        self.char_manager.save_characters()
        self.creature_screen = CreatureScreen(
            self.screen,
            self.current_creature,
            on_battle=self.start_multiplayer,
            on_adventure=self.start_adventure,
            on_main_menu=self.return_to_main_menu
        )
        self.state = "CREATURE_SCREEN"

    def start_creature_selector(self):
        creatures = self.char_manager.get_all_creatures()
        self.char_manager.save_characters()
        self.selector_screen = CreatureSelectorScreen(
            self.screen,
            creatures,
            on_select=self.load_creature_from_selector,
            on_main_menu=self.return_to_main_menu,
            on_delete=self.delete_creature
        )
        self.state = "SELECTOR"

    def load_creature_from_selector(self, creature):
        self.current_creature = creature
        self.char_manager.save_characters()
        self.creature_screen = CreatureScreen(
            self.screen,
            self.current_creature,
            on_battle=self.start_multiplayer,
            on_adventure=self.start_adventure,
            on_main_menu=self.return_to_main_menu
        )
        self.state = "CREATURE_SCREEN"

    def delete_creature(self, creature):
        print(f"[GameEngine] Deleting creature: {creature.creature_type}")
        self.char_manager.delete_creature(creature)

    def start_multiplayer(self):
        from ui.multiplayer_lobby_screen import MultiplayerLobbyScreen
        from network import NetworkClient

        if not self.current_creature:
            print("[Multiplayer] Please create your creature first.")
            return

        network_client = NetworkClient(host='localhost', port=9999)
        try:
            network_client.connect()
        except Exception as e:
            print("[Multiplayer] Failed to connect:", e)
            return

        def on_start_battle(battle_start_data):
            from ui.multiplayer_screen import MultiplayerScreen
            self.multiplayer_screen = MultiplayerScreen(
                self.screen,
                battle_start_data,
                network_client,
                on_main_menu=self.return_to_main_menu,
                on_battle_complete=on_battle_complete
            )
            self.state = "MULTIPLAYER"

        def on_battle_complete():
            self.char_manager.save_characters()
            self.creature_screen = CreatureScreen(
                self.screen,
                self.current_creature,
                on_battle=self.start_multiplayer,
                on_adventure=self.start_adventure,
                on_main_menu=self.return_to_main_menu
            )
            self.state = "CREATURE_SCREEN"
            print("[GameEngine] Battle complete; creature stats saved and loaded into Creature Screen.")

        self.lobby_screen = MultiplayerLobbyScreen(
            self.screen,
            self.current_creature,
            network_client,
            on_start_battle,
            on_main_menu=self.return_to_main_menu
        )
        self.state = "LOBBY"

    def start_adventure(self):
        from ui.adventure_screen import AdventureScreen
        if self.current_creature:
            self.adventure_screen = AdventureScreen(
                self.screen,
                self.current_creature,
                on_main_menu=self.return_to_main_menu,
                on_wild_battle=self.start_wild_battle
            )
            self.state = "ADVENTURE"

    def start_wild_battle(self, wild_creature):
        from ui.battle_screen import BattleScreen
        # Create a Battle instance using the player's creature and the wild enemy.
        from battle_system import Battle
        battle_instance = Battle(self.current_creature, wild_creature)
        self.battle_screen = BattleScreen(
            self.screen,
            battle_instance,
            on_main_menu=self.return_to_main_menu
        )
        self.state = "BATTLE"

    def return_to_main_menu(self):
        self.char_manager.save_characters()
        self.state = "MAIN_MENU"

    def handle_events(self, events):
        if self.state == "MAIN_MENU":
            self.main_menu.handle_events(events, current_creature=self.current_creature)
        elif self.state == "CREATURE_SCREEN":
            self.creature_screen.handle_events(events)
        elif self.state == "BATTLE":
            self.battle_screen.handle_events(events)
        elif self.state == "ADVENTURE":
            self.adventure_screen.handle_events(events)
        elif self.state == "SELECTOR":
            self.selector_screen.handle_events(events)
        elif self.state == "LOBBY":
            self.lobby_screen.handle_events(events)
        elif self.state == "MULTIPLAYER":
            self.multiplayer_screen.handle_events(events)

    def update(self, dt):
        self.autosave_timer += dt / 1000.0
        if self.autosave_timer >= 30:  # autosave every 30 seconds
            self.char_manager.save_characters()
            self.autosave_timer = 0

        if self.state == "MAIN_MENU":
            self.main_menu.update(dt)
        elif self.state == "CREATURE_SCREEN":
            self.creature_screen.update(dt)
        elif self.state == "BATTLE":
            self.battle_screen.update(dt)
        elif self.state == "ADVENTURE":
            self.adventure_screen.update(dt)
        elif self.state == "SELECTOR":
            self.selector_screen.update(dt)
        elif self.state == "LOBBY":
            self.lobby_screen.update(dt)
        elif self.state == "MULTIPLAYER":
            self.multiplayer_screen.update(dt)

    def draw(self):
        if self.state == "MAIN_MENU":
            self.main_menu.draw(current_creature=self.current_creature)
        elif self.state == "CREATURE_SCREEN":
            self.creature_screen.draw()
        elif self.state == "BATTLE":
            self.battle_screen.draw()
        elif self.state == "ADVENTURE":
            self.adventure_screen.draw()
        elif self.state == "SELECTOR":
            self.selector_screen.draw()
        elif self.state == "LOBBY":
            self.lobby_screen.draw()
        elif self.state == "MULTIPLAYER":
            self.multiplayer_screen.draw()
