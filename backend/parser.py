from datetime import datetime

from recipe_scrapers import scrape_html
from recipe_scrapers._exceptions import SchemaOrgException
from ingredient_parser import parse_ingredient

from models import Recipe, RecipeRequest, Ingredient


def optional_value(scraper, method_name: str):
    """Read optional scraper metadata without rejecting an otherwise valid recipe."""
    try:
        return getattr(scraper, method_name)()
    except SchemaOrgException:
        return None

def parse_ingredients(ingredients_list: list[str]) -> list[Ingredient]:
    print("Parsing ingredients list for amounts/units/item names")
    parsed_ingredients = []
    for raw_ingredient in ingredients_list:
        sentence = str(raw_ingredient or "").strip()
        if not sentence:
            continue

        try:
            parsed = parse_ingredient(sentence)
            amount = (getattr(parsed, "amount", None) or [None])[0]
            name = (getattr(parsed, "name", None) or [None])[0]
            parsed_ingredients.append(Ingredient(
                quantity=str(amount.quantity) if amount and amount.quantity is not None else None,
                unit=str(amount.unit) if amount and amount.unit else None,
                amount_text=str(amount.text) if amount and amount.text else None,
                name=str(name.text) if name and name.text else sentence,
                sentence=getattr(parsed, "sentence", None) or sentence,
            ))
        except Exception:
            parsed_ingredients.append(Ingredient(name=sentence, sentence=sentence))

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
        total_time=optional_value(scraper, "total_time"),
        yields=optional_value(scraper, "yields"),
        image=optional_value(scraper, "image"),
        source=request.url,
        date=datetime.now().strftime("%B %d, %Y"),
        datetime=datetime.now().isoformat(),
    )
