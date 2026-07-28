from pydantic import BaseModel

class RecipeRequest(BaseModel):
    url: str
    html: str

# class Ingredient(BaseModel):
#     quantity: float | None = None
#     unit: str | None = None
#     name: str

class Recipe(BaseModel):
    title: str
    ingredients: list[str] #list[Ingredient]
    instructions: list[str]
    total_time: int | None = None
    yields: str | None = None
    image: str | None = None
    source: str