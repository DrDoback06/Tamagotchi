import random
import time
from abilities import generate_random_ability, ability_to_dict
from config import XP_MULTIPLIER, STAT_GROWTH, MAX_AGE

MAX_FEEDS_PER_HOUR = 3
FEED_RESET_INTERVAL = 3600  # seconds

class Creature:
    def __init__(self, chosen_type=None):
        CREATURE_TYPES = {
            "Skeleton": {"hp": 50, "attack": 10, "defense": 5, "speed": 7},
            "Fire Elemental": {"hp": 40, "attack": 12, "defense": 3, "speed": 10},
            "Knight": {"hp": 60, "attack": 8, "defense": 10, "speed": 5},
            "Goblin": {"hp": 45, "attack": 9, "defense": 6, "speed": 9},
            "Troll": {"hp": 70, "attack": 7, "defense": 12, "speed": 4},
        }
        if chosen_type and chosen_type in CREATURE_TYPES:
            self.creature_type = chosen_type
        else:
            self.creature_type = random.choice(list(CREATURE_TYPES.keys()))
        base_stats = CREATURE_TYPES[self.creature_type]
        self.max_hp = base_stats["hp"] + random.randint(-5, 5)
        self.attack = base_stats["attack"] + random.randint(-2, 2)
        self.defense = base_stats["defense"] + random.randint(-2, 2)
        self.speed = base_stats["speed"] + random.randint(-2, 2)
        self.current_hp = self.max_hp
        self.level = 1
        self.xp = 0
        self.evolution_stage = 1
        # Generate exactly 4 abilities
        self.abilities = []
        while len(self.abilities) < 4:
            ab = generate_random_ability(self.creature_type)
            if ab.tier == 1:
                self.abilities.append(ab)
        self.special_ability = self.get_special_ability()
        self.hunger = 0         # 0 to 100
        self.energy = 100       # 0 to 100
        self.age = 0.0          # seconds
        self.is_alive = True

        self.allowed_tier = 1
        self.is_sleeping = False
        self.feed_count = 0
        self.last_feed_time = time.time()
        self.level_just_upgraded = False
        self.pending_skill = None
        self.active_effects = []
        self.inventory = []  # List of items (each is a dict)

        # Mood system: discrete value 0-100 with an ideal value.
        if self.creature_type == "Knight":
            self.ideal_mood = 80
        elif self.creature_type == "Troll":
            self.ideal_mood = 30
        else:
            self.ideal_mood = 50
        self.mood = self.ideal_mood

    def get_special_ability(self):
        if self.creature_type == "Skeleton":
            return "Bone Shield: Reduces incoming damage by 50% for one turn."
        elif self.creature_type == "Fire Elemental":
            return "Inferno Blast: Deals heavy fire damage with a chance to burn."
        elif self.creature_type == "Knight":
            return "Valor Strike: A powerful attack that boosts your attack temporarily."
        elif self.creature_type == "Goblin":
            return "Sneaky Dodge: Greatly increases evasion for one turn."
        elif self.creature_type == "Troll":
            return "Regenerative Smash: Attacks while healing a portion of damage dealt."
        else:
            return "Unknown Special"

    def feed(self):
        current_time = time.time()
        if current_time - self.last_feed_time >= FEED_RESET_INTERVAL:
            self.feed_count = 0
            self.last_feed_time = current_time
        if self.feed_count >= MAX_FEEDS_PER_HOUR:
            print(f"[Feed] {self.creature_type} cannot be fed more now. Try again later.")
            return
        reduction = 40
        self.hunger = max(0, self.hunger - reduction)
        self.feed_count += 1
        self.mood = min(100, self.mood + 5)
        print(f"[Feed] {self.creature_type} fed. Hunger: {self.hunger}, Mood: {self.mood} (Feed count: {self.feed_count}).")

    def sleep(self):
        self.is_sleeping = True
        print(f"[Sleep] {self.creature_type} is now sleeping.")

    def wake_up(self):
        self.is_sleeping = False
        print(f"[Sleep] {self.creature_type} woke up.")

    def update_needs(self, dt):
        if self.is_sleeping:
            energy_regen_rate = 100 / 60.0  # full energy in 60 sec
            hunger_rate = 100 / 3600.0       # slow hunger increase
            health_regen_rate = self.max_hp / 180.0  # regain full HP in 3 minutes
            self.energy = min(100, self.energy + energy_regen_rate * (dt / 1000.0))
            self.hunger += hunger_rate * (dt / 1000.0)
            self.current_hp = min(self.max_hp, self.current_hp + health_regen_rate * (dt / 1000.0))
        else:
            energy_loss_rate = 100 / 600.0  # lose full energy in 600 sec
            hunger_rate = 100 / 300.0       # hunger increases in 300 sec
            self.energy = max(0, self.energy - energy_loss_rate * (dt / 1000.0))
            self.hunger += hunger_rate * (dt / 1000.0)
        if self.hunger > 100:
            self.hunger = 100
        hunger_threshold = 70
        if self.hunger >= hunger_threshold and self.creature_type != "Skeleton":
            health_loss = (self.hunger - hunger_threshold) * 0.1 * (dt / 1000.0)
            self.current_hp = max(0, self.current_hp - health_loss)
            if self.current_hp == 0:
                self.is_alive = False
                print(f"[Death] {self.creature_type} died due to extreme hunger.")

    def update_age(self, dt):
        if self.is_alive:
            self.age += dt / 1000.0
            if self.age >= MAX_AGE:
                self.is_alive = False
                print(f"[Death] {self.creature_type} died of old age at {self.age:.1f} sec!")
                from database import save_dead_creature
                save_dead_creature(self)

    def update_effects(self):
        new_effects = []
        for effect in self.active_effects:
            effect["duration"] -= 1
            if effect["duration"] > 0:
                new_effects.append(effect)
        self.active_effects = new_effects

    def add_effect(self, effect):
        self.active_effects.append(effect)
        print(f"[Effect] {self.creature_type} gains effect: {effect}")

    @property
    def wellness(self):
        hp_ratio = self.current_hp / self.max_hp
        energy_ratio = self.energy / 100.0
        hunger_ratio = 1 - (self.hunger / 100.0)
        overall = (hp_ratio + energy_ratio + hunger_ratio) / 3 * 100
        return int(overall)

    def gain_xp(self, amount):
        self.xp += amount
        xp_threshold = self.level * XP_MULTIPLIER
        if self.xp >= xp_threshold:
            self.level_up()

    def lose_xp(self, amount):
        self.xp -= amount
        while self.xp < 0 and self.level > 1:
            self.level -= 1
            self.xp += self.level * XP_MULTIPLIER
            print(f"[XP Loss] {self.creature_type} dropped to Level {self.level}!")
            self.remove_high_level_abilities()

    def level_up(self):
        self.level += 1
        self.xp = 0
        hp_inc = random.randint(*STAT_GROWTH["hp"])
        atk_inc = random.randint(*STAT_GROWTH["attack"])
        def_inc = random.randint(*STAT_GROWTH["defense"])
        spd_inc = random.randint(*STAT_GROWTH["speed"])
        self.max_hp += hp_inc
        self.attack += atk_inc
        self.defense += def_inc
        self.speed += spd_inc
        self.current_hp = self.max_hp
        print(f"[Level Up] {self.creature_type} reached Level {self.level}! (+HP:{hp_inc}, +Atk:{atk_inc}, +Def:{def_inc}, +Spd:{spd_inc})")
        self.level_just_upgraded = True
        self.pending_skill = generate_random_ability(self.creature_type)

    def assign_random_skill(self):
        new_ability = generate_random_ability(self.creature_type)
        self.abilities.append(new_ability)
        if len(self.abilities) > 4:
            removed = self.abilities.pop(0)
            print(f"[Ability Update] Removed {removed} to add new ability: {new_ability}")
        else:
            print(f"[Ability Update] Added new ability: {new_ability}")

    def remove_high_level_abilities(self):
        filtered = []
        for ability in self.abilities:
            if hasattr(ability, 'min_level') and ability.min_level > self.level:
                print(f"[Forget Ability] {self.creature_type} forgot {ability} due to level drop.")
            else:
                filtered.append(ability)
        self.abilities = filtered

    def add_item(self, item):
        for inv_item in self.inventory:
            if inv_item["name"] == item["name"]:
                inv_item["quantity"] += item["quantity"]
                print(f"[Inventory] Added {item['quantity']} {item['name']}(s). Total now: {inv_item['quantity']}.")
                return
        self.inventory.append(item)
        print(f"[Inventory] New item added: {item['name']} (x{item['quantity']}).")

    def use_item(self, item_name):
        for inv_item in self.inventory:
            if inv_item["name"] == item_name and inv_item["quantity"] > 0:
                effect = inv_item["effect"]
                if effect["type"] == "heal":
                    self.current_hp = min(self.max_hp, self.current_hp + effect["amount"])
                    print(f"[Inventory] Used {item_name}: Healed {effect['amount']} HP.")
                elif effect["type"] == "energy":
                    self.energy = min(100, self.energy + effect["amount"])
                    print(f"[Inventory] Used {item_name}: Restored {effect['amount']} energy.")
                elif effect["type"] == "mood":
                    self.mood = max(0, min(100, self.mood + effect["amount"]))
                    print(f"[Inventory] Used {item_name}: Mood changed by {effect['amount']}.")
                inv_item["quantity"] -= 1
                return True
        print(f"[Inventory] Item {item_name} not available.")
        return False

    def to_dict(self):
        return {
            "creature_type": self.creature_type,
            "max_hp": self.max_hp,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "current_hp": self.current_hp,
            "level": self.level,
            "xp": self.xp,
            "evolution_stage": self.evolution_stage,
            "age": self.age,
            "is_alive": self.is_alive,
            "hunger": self.hunger,
            "energy": self.energy,
            "abilities": [ability_to_dict(a) for a in self.abilities],
            "special_ability": self.special_ability,
            "inventory": self.inventory
        }

    def __str__(self):
        abilities_str = "\n  ".join([str(a) for a in self.abilities])
        return (f"Creature: {self.creature_type} (Stage {self.evolution_stage})\n"
                f"Level: {self.level} | XP: {self.xp}/{self.level * XP_MULTIPLIER}\n"
                f"HP: {int(self.current_hp)}/{self.max_hp} | Atk: {self.attack} | Def: {self.defense} | Spd: {self.speed}\n"
                f"Energy: {int(self.energy)} | Hunger: {int(self.hunger)} | Age: {int(self.age)} sec\n"
                f"Wellness: {self.wellness}% | Mood: {self.mood}/100\n"
                f"Special: {self.special_ability}\n"
                f"Abilities:\n  {abilities_str}\n"
                f"Inventory: {self.inventory}\n")

if __name__ == "__main__":
    creature = Creature()
    print(creature)
    creature.gain_xp(150)
    print(creature)
