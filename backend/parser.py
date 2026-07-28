from recipe_scrapers import scrape_html

from models import Recipe, RecipeRequest

def parse_recipe(request: RecipeRequest):

    scraper = scrape_html(
        request.html,
        org_url=request.url
    )

    return Recipe(
        title=scraper.title(),
        ingredients=scraper.ingredients(),
        instructions=scraper.instructions_list(),
        total_time=scraper.total_time(),
        yields=scraper.yields(),
        image=scraper.image(),
        source=request.url
    )