from fastapi import FastAPI

from models import RecipeRequest
from parser import parse_recipe
from storage import save_recipe

app = FastAPI()

@app.post("/save")
def save(request: RecipeRequest):
    # Parse the recipe from the request
    recipe = parse_recipe(request)

    # Save the recipe to storage
    save_recipe(recipe)

    return {
        "status": "success"
    }