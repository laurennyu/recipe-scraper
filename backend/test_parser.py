import os
from unittest.mock import patch

from models import RecipeRequest
from parser import fetch_recipe_html, parse_recipe

url = "https://tastesbetterfromscratch.com/easy-tiramisu/"

with open("tiramisu.html", "r", encoding="utf-8") as f:
    html = f.read()

recipe = parse_recipe(RecipeRequest(url=url, html=html))

print(recipe)


def test_fetch_recipe_html_reads_page_content():
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"<html><body><h1>Recipe</h1></body></html>"

    with patch("parser.urlopen", return_value=FakeResponse()):
        assert fetch_recipe_html("https://example.com/recipe") == "<html><body><h1>Recipe</h1></body></html>"