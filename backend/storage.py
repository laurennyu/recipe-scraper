import hashlib
import json
import re
import unicodedata
from pathlib import Path

from models import Recipe

RECIPES_DIR = Path(__file__).resolve().parent.parent / "recipes"
ACCOUNTS_DIR = RECIPES_DIR / "accounts"
USERS_FILE = RECIPES_DIR / "users.json"


def _ensure_storage() -> None:
    RECIPES_DIR.mkdir(exist_ok=True)
    ACCOUNTS_DIR.mkdir(exist_ok=True)


def normalize_username(username: str) -> str:
    """Return a display-safe local username or raise ValueError."""
    normalized = " ".join(username.strip().split())
    if not 1 <= len(normalized) <= 50:
        raise ValueError("Username must be between 1 and 50 characters.")
    if any(ord(character) < 32 for character in normalized):
        raise ValueError("Username contains an invalid character.")
    return normalized


def _read_users() -> dict[str, dict[str, str]]:
    _ensure_storage()
    if not USERS_FILE.exists():
        return {}
    try:
        with USERS_FILE.open(encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write_users(users: dict[str, dict[str, str]]) -> None:
    _ensure_storage()
    with USERS_FILE.open("w", encoding="utf-8") as file:
        json.dump(users, file, indent=2, ensure_ascii=False)


def _folder_name(username: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", username).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.casefold()).strip("-") or "user"
    digest = hashlib.sha256(username.casefold().encode("utf-8")).hexdigest()[:10]
    return f"{slug[:36]}-{digest}"


def select_user(username: str) -> dict[str, str]:
    """Find or create a username-to-folder mapping, then return it."""
    display_name = normalize_username(username)
    key = display_name.casefold()
    users = _read_users()
    account = users.get(key)
    if account is None:
        account = {"username": display_name, "folder": _folder_name(display_name)}
        users[key] = account
        _write_users(users)
    (ACCOUNTS_DIR / account["folder"]).mkdir(parents=True, exist_ok=True)
    return account


def list_users() -> list[dict[str, str]]:
    return sorted(_read_users().values(), key=lambda account: account["username"].casefold())


def recipe_directory(username: str) -> Path:
    account = select_user(username)
    return ACCOUNTS_DIR / account["folder"]


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


def save_recipe(recipe: Recipe, username: str):
    ensure_ingredient_ids(recipe)
    path = recipe_directory(username) / f"{recipe.title}.json"
    with path.open("w", encoding="utf-8") as file:
        json.dump(recipe.model_dump(), file, indent=4, ensure_ascii=False)


def update_recipe(original_title: str, recipe: Recipe, username: str):
    """Save an edited recipe, removing the old file if it was renamed."""
    directory = recipe_directory(username)
    original_path = directory / f"{original_title}.json"
    new_path = directory / f"{recipe.title}.json"
    if original_path != new_path and new_path.exists():
        raise FileExistsError(f"A recipe named {recipe.title!r} already exists.")
    save_recipe(recipe, username)
    if original_path != new_path and original_path.exists():
        original_path.unlink()


def list_recipes(username: str) -> list[Recipe]:
    """Load a user's valid locally stored recipes, ordered by name."""
    recipes = []
    for path in recipe_directory(username).glob("*.json"):
        try:
            with path.open(encoding="utf-8") as file:
                recipes.append(Recipe.model_validate(json.load(file)))
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(f"Skipping unreadable recipe file {path}: {error}")
    return sorted(recipes, key=lambda recipe: recipe.title.casefold())
