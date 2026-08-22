from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from models import Recipe, RecipeRequest, RecipeUpdateRequest
from parser import parse_recipe
from storage import list_recipes, save_recipe, update_recipe

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


@app.post("/api/recipes/update", response_model=Recipe)
def update_saved_recipe(request: RecipeUpdateRequest):
    """Persist edits made from the dashboard."""
    try:
        update_recipe(request.original_title, request.recipe)
    except FileExistsError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return request.recipe

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
