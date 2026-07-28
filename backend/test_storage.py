from models import Recipe, Ingredient
from storage import save_recipe

recipe = Recipe(
    title="Test Recipe",
    ingredients=[
        Ingredient(name="Sugar")
    ],
    instructions=["Mix."],
    source="test"
)

# print(recipe.model_dump())
save_recipe(recipe)