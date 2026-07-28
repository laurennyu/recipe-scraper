import json
from pathlib import Path

SAVE_DIR = Path("../recipes")
SAVE_DIR.mkdir(exist_ok=True)

def save_recipe(recipe):
    filename = recipe["title"] + ".json"
    path = SAVE_DIR / filename

    with open(path, "w") as f:
        json.dump(
            recipe,
            f,
            indent=4
        )