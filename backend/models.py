from pydantic import BaseModel

class RecipeRequest(BaseModel):
    url: str
    html: str

class Ingredient(BaseModel):
    quantity: str | None = None
    unit: str | None = None
    amount_text: str | None = None
    name: str

class Recipe(BaseModel):
    title: str
    ingredients: list[Ingredient]
    instructions: list[str]
    total_time: int | None = None
    yields: str | None = None
    image: str | None = None
    source: str
    date: str | None = None
    datetime: str | None = None
    tried: bool | None = None
    rating: int | None = None
    tags: str | None = None
    notes: str | None = None