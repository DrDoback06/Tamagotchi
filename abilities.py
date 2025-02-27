# abilities.py

import random

class Ability:
    def __init__(self, name, base_damage, ability_type, tier=1, min_level=1,
                 energy_cost=10, effect_value=0, duration=0, cooldown=0):
        """
        :param name: Name of the ability.
        :param base_damage: Base damage for damage abilities.
        :param ability_type: "damage", "buff", "debuff", "heal", or "status".
        :param tier: Tier of the ability.
        :param min_level: Minimum creature level required.
        :param energy_cost: Energy cost to use the ability.
        :param effect_value: Magnitude of the effect (e.g., 0.2 for +20%).
        :param duration: Duration of effect in turns (0 means instant).
        :param cooldown: Cooldown in turns.
        """
        self.name = name
        self.base_damage = base_damage
        self.ability_type = ability_type
        self.tier = tier
        self.min_level = min_level
        self.energy_cost = energy_cost
        self.effect_value = effect_value
        self.duration = duration
        self.cooldown = cooldown
        self.damage = self.calculate_damage()

    def calculate_damage(self):
        multiplier = 1 + (self.tier - 1) * 0.2
        return int(self.base_damage * multiplier)

    def apply_effect(self, attacker, defender, battle):
        """
        Apply additional effect:
         - "buff": boosts attacker stat.
         - "debuff": reduces defender stat.
         - "heal": restores HP.
         - "status": e.g., stun.
        """
        if self.ability_type == "buff":
            attacker.add_effect({"stat": "attack", "multiplier": 1 + self.effect_value, "duration": self.duration})
        elif self.ability_type == "debuff":
            defender.add_effect({"stat": "defense", "multiplier": max(0, 1 - self.effect_value), "duration": self.duration})
        elif self.ability_type == "heal":
            attacker.current_hp = min(attacker.max_hp, attacker.current_hp + self.effect_value)
        elif self.ability_type == "status":
            defender.add_effect({"status": "stun", "duration": self.duration})
        # Extend with more effect types as needed.

    def __str__(self):
        return (f"{self.name} (Tier {self.tier}) - Damage: {self.damage} "
                f"(Cost: {self.energy_cost} energy, Min Lvl: {self.min_level})")

def ability_to_dict(ability):
    return {
        "name": ability.name,
        "base_damage": ability.base_damage,
        "ability_type": ability.ability_type,
        "tier": ability.tier,
        "min_level": ability.min_level,
        "energy_cost": ability.energy_cost,
        "effect_value": ability.effect_value,
        "duration": ability.duration,
        "cooldown": ability.cooldown
    }

def ability_from_dict(d):
    return Ability(
        d["name"],
        d["base_damage"],
        d["ability_type"],
        d.get("tier", 1),
        d.get("min_level", 1),
        d.get("energy_cost", 10),
        d.get("effect_value", 0),
        d.get("duration", 0),
        d.get("cooldown", 0)
    )

# Base ability pools per creature type.
BASE_ABILITY_POOLS = {
    "Skeleton": [
        {"name": "Bone Smash", "base_damage": 10, "ability_type": "damage", "min_level": 1},
        {"name": "Haunting Howl", "base_damage": 8, "ability_type": "debuff", "min_level": 1, "effect_value": 0.2, "duration": 2},
    ],
    "Fire Elemental": [
        {"name": "Flame Burst", "base_damage": 12, "ability_type": "damage", "min_level": 1},
        {"name": "Scorch", "base_damage": 9, "ability_type": "debuff", "min_level": 1, "effect_value": 0.3, "duration": 2},
    ],
    "Knight": [
        {"name": "Sword Slash", "base_damage": 11, "ability_type": "damage", "min_level": 1},
        {"name": "Shield Bash", "base_damage": 8, "ability_type": "debuff", "min_level": 1, "effect_value": 0.25, "duration": 2},
    ],
    "Goblin": [
        {"name": "Sneak Attack", "base_damage": 10, "ability_type": "damage", "min_level": 1},
        {"name": "Panic", "base_damage": 7, "ability_type": "status", "min_level": 1, "duration": 1},
    ],
    "Troll": [
        {"name": "Club Smash", "base_damage": 13, "ability_type": "damage", "min_level": 1},
        {"name": "Roar", "base_damage": 5, "ability_type": "debuff", "min_level": 1, "effect_value": 0.2, "duration": 2},
    ]
}

NORMAL_ABILITY_POOL = [
    {"name": "Quick Strike", "base_damage": 8, "ability_type": "damage", "min_level": 1},
    {"name": "Focus", "base_damage": 0, "ability_type": "buff", "min_level": 1, "effect_value": 0.2, "duration": 1},
]

def get_random_tier():
    roll = random.random()
    if roll < 0.7:
        return 1
    elif roll < 0.9:
        return 2
    else:
        return 3

def generate_random_ability(creature_type):
    pool = BASE_ABILITY_POOLS.get(creature_type, []) + NORMAL_ABILITY_POOL
    chosen = random.choice(pool)
    tier = get_random_tier()
    if tier > 1:  # For new creatures, force tier 1.
        tier = 1
    return Ability(
        chosen["name"],
        chosen["base_damage"],
        chosen["ability_type"],
        tier,
        chosen.get("min_level", 1),
        chosen.get("energy_cost", 10),
        chosen.get("effect_value", 0),
        chosen.get("duration", 0),
        chosen.get("cooldown", 0)
    )
