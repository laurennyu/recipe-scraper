from fastapi import FastAPI
from pydantic import BaseModel

from parser import parse_recipe
from storage import save_recipe

app = FastAPI()

class RecipeRequest(BaseModel):
    url: str
    html: str

@app.post("/save")
def save(request: RecipeRequest):

    recipe = parse_recipe(
        request.url,
        request.html
    )

    save_recipe(recipe)

    return {
        "status": "success"
    }