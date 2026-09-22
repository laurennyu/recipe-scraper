from pathlib import Path
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from models import Recipe, RecipeRequest, RecipeUpdateRequest
from parser import parse_recipe
from storage import list_recipes, list_users, normalize_username, save_recipe, select_user, update_recipe

app = FastAPI()

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


def current_username(
    x_recipe_username: str | None = Header(default=None),
    username_query: str | None = Query(default=None, alias="username"),
) -> str:
    username = x_recipe_username or username_query
    if not username:
        raise HTTPException(status_code=400, detail="Choose a username first.")
    try:
        return normalize_username(username)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.get("/api/users")
def users():
    return list_users()


@app.post("/api/users/select")
def select_account(username: str):
    try:
        return select_user(username)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.get("/api/recipes", response_model=list[Recipe])
def recipes(username: str = Depends(current_username)):
    """Return locally stored recipes for the dashboard."""
    return list_recipes(username)


@app.post("/api/recipes/update", response_model=Recipe)
def update_saved_recipe(request: RecipeUpdateRequest, username: str = Depends(current_username)):
    """Persist edits made from the dashboard."""
    try:
        update_recipe(request.original_title, request.recipe, username)
    except FileExistsError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return request.recipe

@app.post("/preview")
def preview(request: RecipeRequest):
    recipe = parse_recipe(request)
    return recipe.model_dump()

@app.post("/save")
def save(recipe: Recipe, username: str = Depends(current_username)):
    """Persist the recipe returned by /preview without parsing its HTML again."""
    save_recipe(recipe, username)

    return {
        "status": "success",
        "recipe": recipe.model_dump()
    }
