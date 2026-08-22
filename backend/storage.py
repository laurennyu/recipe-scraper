import json
from pathlib import Path

from models import Recipe

SAVE_DIR = Path(__file__).resolve().parent.parent / "recipes"
SAVE_DIR.mkdir(exist_ok=True)


def ensure_ingredient_ids(recipe: Recipe):
    """Assign stable IDs to ingredients that do not already have one."""
    used_ids = set()
    next_id = 0

    for ingredient in recipe.ingredients:
        if ingredient.id is None or ingredient.id in used_ids:
            while next_id in used_ids:
                next_id += 1
            ingredient.id = next_id
            next_id += 1
        used_ids.add(ingredient.id)


def save_recipe(recipe: Recipe):
    ensure_ingredient_ids(recipe)
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


def update_recipe(original_title: str, recipe: Recipe):
    """Save an edited recipe, removing the old file if it was renamed."""
    original_path = SAVE_DIR / f"{original_title}.json"
    new_path = SAVE_DIR / f"{recipe.title}.json"

    if original_path != new_path and new_path.exists():
        raise FileExistsError(f"A recipe named {recipe.title!r} already exists.")

    save_recipe(recipe)
    if original_path != new_path and original_path.exists():
        original_path.unlink()


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
