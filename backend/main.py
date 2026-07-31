from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import Recipe, RecipeRequest
from parser import parse_recipe
from storage import save_recipe

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Fine for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/preview")
def preview(request: RecipeRequest):
    recipe = parse_recipe(request)
    return recipe.model_dump()

@app.post("/save")
def save(recipe: Recipe):
    """Persist the recipe returned by /preview without parsing its HTML again."""
    save_recipe(recipe)

    return {
        "status": "success",
        "recipe": recipe.model_dump()
    }
