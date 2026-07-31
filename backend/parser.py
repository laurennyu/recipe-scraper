from datetime import datetime

from recipe_scrapers import scrape_html
from ingredient_parser import parse_ingredient

from models import Recipe, RecipeRequest, Ingredient

def parse_ingredients(ingredients_list: list[str]) -> list[Ingredient]:
    print("Parsing ingredients list for amounts/units/item names")
    # Parse each ingredient in the list
    parsed_ingredients = [parse_ingredient(ingredient) for ingredient in ingredients_list]
    print(parsed_ingredients)

    parsed_ingredients = [Ingredient(quantity=str(ingredient.amount[0].quantity) if ingredient.amount else None,
                                     unit=str(ingredient.amount[0].unit) if ingredient.amount else None,
                                     name=ingredient.name[0].text)
                                     for ingredient in parsed_ingredients]
    # TODO: Add error handling

    print("Parsed ingredients:", parsed_ingredients)
    return parsed_ingredients

def parse_recipe(request: RecipeRequest):
    # Scrape the recipe from the HTML content
    scraper = scrape_html(
        request.html,
        org_url=request.url
    )

    # Parse the ingredients
    ingredients_list = parse_ingredients(scraper.ingredients())

    # Return a Recipe object with the scraped data
    return Recipe(
        title=scraper.title(),
        ingredients=ingredients_list,
        instructions=scraper.instructions_list(),
        total_time=scraper.total_time(),
        yields=scraper.yields(),
        image=scraper.image(),
        source=request.url,
        date=datetime.now().strftime("%B %d, %Y"),
        datetime=datetime.now().isoformat(),
    )