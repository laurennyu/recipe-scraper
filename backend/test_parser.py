import os
from models import RecipeRequest
from parser import parse_recipe

url = "https://tastesbetterfromscratch.com/easy-tiramisu/"

with open("tiramisu.html", "r", encoding="utf-8") as f:
    html = f.read()

recipe = parse_recipe(RecipeRequest(url=url, html=html))

print(recipe)