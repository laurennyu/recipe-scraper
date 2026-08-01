import json
import os
from pathlib import Path

from models import Recipe

SAVE_DIR = Path(os.path.abspath("../recipes"))
SAVE_DIR.mkdir(exist_ok=True)

def save_recipe(recipe: Recipe):
    filename = recipe.title + ".json"
    path = os.path.join(SAVE_DIR, filename)
    print(f"Saving recipe {recipe.title} to {path}")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            recipe.model_dump(),
            f,
            indent=4,
            ensure_ascii=False,
        )
        print(f"Recipe {recipe.title} saved to {path}")
