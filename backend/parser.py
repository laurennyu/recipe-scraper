from recipe_scrapers import scrape_html

def parse_recipe(url, html):

    scraper = scrape_html(
        html,
        org_url=url
    )

    return {
        "title": scraper.title(),
        "ingredients": scraper.ingredients(),
        "instructions": scraper.instructions(),
        "total_time": scraper.total_time(),
        "yields": scraper.yields(),
        "image": scraper.image(),
        "author": scraper.author()
    }