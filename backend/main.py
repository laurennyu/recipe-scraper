from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from models import Recipe, RecipeRequest
from parser import parse_recipe
from storage import list_recipes, save_recipe

app = FastAPI()
PROJECT_DIR = Path(__file__).resolve().parent.parent

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Fine for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(PROJECT_DIR / "dashboard.html")


@app.get("/api/recipes", response_model=list[Recipe])
def recipes():
    """Return locally stored recipes for the dashboard."""
    return list_recipes()

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
