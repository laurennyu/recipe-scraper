import hashlib
import json
import logging
import os
import re
import unicodedata
from pathlib import Path

from dotenv import load_dotenv

from models import Recipe

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Local filesystem defaults
RECIPES_DIR = Path(__file__).resolve().parent.parent / "recipes"
ACCOUNTS_DIR = RECIPES_DIR / "accounts"
USERS_FILE = RECIPES_DIR / "users.json"

# Optional Supabase configuration (server-side service role key expected)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)

logger.info(
    "Supabase env status: url_present=%s, key_present=%s, use_supabase=%s",
    bool(SUPABASE_URL),
    bool(SUPABASE_SERVICE_ROLE_KEY),
    USE_SUPABASE,
)

_supabase = None
if USE_SUPABASE:
    logger.info("Using Supabase storage backend")
    try:
        from supabase import create_client
    except Exception as exc:  # pragma: no cover - only triggers when env set but package missing
        raise RuntimeError(
            "SUPABASE env vars are set but the 'supabase' Python package is not installed."
        ) from exc

    _supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
else:
    logger.info("Using local filesystem storage backend")


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
    # Supabase-backed account
    if USE_SUPABASE:
        res = _supabase.table("accounts").select("id,username").eq("username_key", key).limit(1).execute()
        data = getattr(res, "data", None) or (res.get("data") if isinstance(res, dict) else None)
        if not data:
            insert = _supabase.table("accounts").insert({"username": display_name, "username_key": key}).execute()
            data = getattr(insert, "data", None) or (insert.get("data") if isinstance(insert, dict) else None)
        account_row = data[0]
        # Maintain API compatibility: return a dict with `username` and `folder`.
        # `folder` contains the Supabase account `id` when using Supabase.
        return {"username": account_row["username"], "folder": account_row["id"]}

    users = _read_users()
    account = users.get(key)
    if account is None:
        account = {"username": display_name, "folder": _folder_name(display_name)}
        users[key] = account
        _write_users(users)
    (ACCOUNTS_DIR / account["folder"]).mkdir(parents=True, exist_ok=True)
    return account


def list_users() -> list[dict[str, str]]:
    if USE_SUPABASE:
        res = _supabase.table("accounts").select("id,username").order("username", desc=False).execute()
        data = getattr(res, "data", None) or (res.get("data") if isinstance(res, dict) else None) or []
        return sorted([{"username": row["username"], "folder": row["id"]} for row in data], key=lambda account: account["username"].casefold())

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
    if USE_SUPABASE:
        account = select_user(username)
        account_id = account["folder"]
        payload = recipe.model_dump()
        # Try updating an existing row first; if none updated, insert a new row.
        update_res = _supabase.table("recipes").update({"recipe": payload}).eq("account_id", account_id).eq("title", recipe.title).execute()
        update_data = getattr(update_res, "data", None) or (update_res.get("data") if isinstance(update_res, dict) else None) or []
        if not update_data:
            _supabase.table("recipes").insert({"account_id": account_id, "title": recipe.title, "recipe": payload}).execute()
        return

    path = recipe_directory(username) / f"{recipe.title}.json"
    with path.open("w", encoding="utf-8") as file:
        json.dump(recipe.model_dump(), file, indent=4, ensure_ascii=False)


def update_recipe(original_title: str, recipe: Recipe, username: str):
    """Save an edited recipe, removing the old file if it was renamed."""
    if USE_SUPABASE:
        account = select_user(username)
        account_id = account["folder"]
        # If renaming, ensure new title doesn't already exist
        if original_title != recipe.title:
            exists_res = _supabase.table("recipes").select("id").eq("account_id", account_id).eq("title", recipe.title).limit(1).execute()
            exists = getattr(exists_res, "data", None) or (exists_res.get("data") if isinstance(exists_res, dict) else None) or []
            if exists:
                raise FileExistsError(f"A recipe named {recipe.title!r} already exists.")
        # Update the existing row
        _supabase.table("recipes").update({"title": recipe.title, "recipe": recipe.model_dump()}).eq("account_id", account_id).eq("title", original_title).execute()
        return

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
    if USE_SUPABASE:
        account = select_user(username)
        account_id = account["folder"]
        res = _supabase.table("recipes").select("recipe,title").eq("account_id", account_id).order("title", desc=False).execute()
        data = getattr(res, "data", None) or (res.get("data") if isinstance(res, dict) else None) or []
        recipes = []
        for row in data:
            try:
                recipes.append(Recipe.model_validate(row.get("recipe") or row.get("recipe")))
            except Exception as error:  # pragma: no cover - runtime sanity
                print(f"Skipping unreadable recipe row for account {account_id}: {error}")
        return sorted(recipes, key=lambda recipe: recipe.title.casefold())

    recipes = []
    for path in recipe_directory(username).glob("*.json"):
        try:
            with path.open(encoding="utf-8") as file:
                recipes.append(Recipe.model_validate(json.load(file)))
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(f"Skipping unreadable recipe file {path}: {error}")
    return sorted(recipes, key=lambda recipe: recipe.title.casefold())
