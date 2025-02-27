# battle_system.py

import random

class Battle:
    def __init__(self, player_creature, enemy_creature):
        self.player = player_creature
        self.enemy = enemy_creature
        self.turn = "player"  # 'player' or 'enemy'
        self.battle_over = False
        self.winner = None
        self.message = "Battle start!"

    def calculate_damage(self, attacker, defender, ability):
        raw_damage = ability.damage + attacker.attack - int(defender.defense * 0.5)
        return max(1, raw_damage)

    def apply_attack(self, attacker, defender, ability_index):
        # Basic checks
        if ability_index < 0 or ability_index >= len(attacker.abilities):
            self.message = "Invalid ability selection!"
            return
        ability = attacker.abilities[ability_index]

        if ability.tier > getattr(attacker, 'allowed_tier', 1):
            self.message = f"Cannot use {ability.name}: tier {ability.tier} > allowed tier {attacker.allowed_tier}!"
            return
        if attacker.energy < ability.energy_cost:
            self.message = f"Not enough energy to use {ability.name} (cost {ability.energy_cost})!"
            return

        # Deduct energy and apply damage
        attacker.energy -= ability.energy_cost
        damage = self.calculate_damage(attacker, defender, ability)
        defender.current_hp -= damage
        self.message = f"{attacker.creature_type} used {ability.name} for {damage} damage!"

        # If ability has an effect, apply it
        if ability.duration > 0 and ability.effect_value:
            ability.apply_effect(attacker, defender, self)

        # Check if defender died
        if defender.current_hp <= 0:
            defender.current_hp = 0
            self.battle_over = True
            self.winner = "player" if attacker == self.player else "enemy"

    def enemy_turn(self):
        """
        Called after the player attacks if the battle isn't over.
        Enemy picks a random ability index and attacks the player.
        """
        if self.battle_over:
            return
        # Randomly pick an ability from enemy's list
        if len(self.enemy.abilities) == 0:
            self.message = f"{self.enemy.creature_type} has no abilities!"
            return
        ability_index = random.randint(0, len(self.enemy.abilities) - 1)
        self.apply_attack(self.enemy, self.player, ability_index)
        # Switch turn back to player if the battle isn't over
        if not self.battle_over:
            self.turn = "player"
