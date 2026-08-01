import json
from pathlib import Path

from models import Recipe

SAVE_DIR = Path(__file__).resolve().parent.parent / "recipes"
SAVE_DIR.mkdir(exist_ok=True)

def save_recipe(recipe: Recipe):
    filename = recipe.title + ".json"
    path = SAVE_DIR / filename
    print(f"Saving recipe {recipe.title} to {path}")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            recipe.model_dump(),
            f,
            indent=4,
            ensure_ascii=False,
        )
        print(f"Recipe {recipe.title} saved to {path}")


def list_recipes() -> list[Recipe]:
    """Load every valid recipe stored locally, ordered by name."""
    recipes = []

    for path in SAVE_DIR.glob("*.json"):
        try:
            with path.open(encoding="utf-8") as file:
                recipes.append(Recipe.model_validate(json.load(file)))
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(f"Skipping unreadable recipe file {path}: {error}")

    return sorted(recipes, key=lambda recipe: recipe.title.casefold())
