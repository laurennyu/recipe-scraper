from pathlib import Path

from models import Ingredient, Recipe
import storage


def configure_storage(tmp_path: Path, monkeypatch) -> None:
    recipes_dir = tmp_path / "recipes"
    monkeypatch.setattr(storage, "RECIPES_DIR", recipes_dir)
    monkeypatch.setattr(storage, "ACCOUNTS_DIR", recipes_dir / "accounts")
    monkeypatch.setattr(storage, "USERS_FILE", recipes_dir / "users.json")


def recipe(title: str) -> Recipe:
    return Recipe(title=title, ingredients=[Ingredient(name="Sugar")], instructions=["Mix."], source="test")


def test_user_mapping_is_stable_and_uses_a_safe_folder(tmp_path, monkeypatch):
    configure_storage(tmp_path, monkeypatch)

    first = storage.select_user("  Alice Smith  ")
    second = storage.select_user("alice smith")

    assert first == second
    assert first["username"] == "Alice Smith"
    assert "/" not in first["folder"]
    assert (storage.ACCOUNTS_DIR / first["folder"]).is_dir()


def test_recipes_are_separated_by_username(tmp_path, monkeypatch):
    configure_storage(tmp_path, monkeypatch)

    storage.save_recipe(recipe("Alice recipe"), "Alice")
    storage.save_recipe(recipe("Bob recipe"), "Bob")

    assert [item.title for item in storage.list_recipes("Alice")] == ["Alice recipe"]
    assert [item.title for item in storage.list_recipes("Bob")] == ["Bob recipe"]
