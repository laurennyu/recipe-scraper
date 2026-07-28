from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import RecipeRequest
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

@app.post("/save")
def save(request: RecipeRequest):
    # Parse the recipe from the request
    recipe = parse_recipe(request)

    # Save the recipe to storage
    save_recipe(recipe)

    return {
        "status": "success"
    }