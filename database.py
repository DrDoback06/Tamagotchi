# database.py
import json
import os

DEAD_CREATURES_FILE = "dead_creatures.json"
CREATURES_FILE = "creatures.json"

def save_dead_creature(creature):
    creature_data = creature.to_dict()
    if os.path.exists(DEAD_CREATURES_FILE):
        with open(DEAD_CREATURES_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(creature_data)
    with open(DEAD_CREATURES_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_creature_list(creatures, filename=CREATURES_FILE):
    data = [creature.to_dict() for creature in creatures]
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_creature_list(filename=CREATURES_FILE):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print("[Database] No creature data found:", e)
        return []
