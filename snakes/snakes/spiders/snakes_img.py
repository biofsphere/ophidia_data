from pathlib import Path
from urllib.parse import parse_qs, urlparse

import scrapy


class SnakesImgSpider(scrapy.Spider):
    name = "snakesimg"

    def start_requests(self):
        urls = [
            "https://reptile-database.reptarium.cz/species?genus=Apostolepis&species=dimidiata&search_param=%28%28taxon%3D%27snake%27%29%28reference%3D%27Rio+Grande+do+Sul%27%29%29",
            "https://reptile-database.reptarium.cz/species?genus=Atractus&species=paraguayensis&search_param=%28%28taxon%3D%27snake%27%29%28reference%3D%27Rio+Grande+do+Sul%27%29%29",
            "https://reptile-database.reptarium.cz/species?genus=Atractus&species=reticulatus&search_param=%28%28taxon%3D%27snake%27%29%28reference%3D%27Rio+Grande+do+Sul%27%29%29",
            "https://reptile-database.reptarium.cz/species?genus=Atractus&species=zebrinus&search_param=%28%28taxon%3D%27snake%27%29%28reference%3D%27Rio+Grande+do+Sul%27%29%29",
            "https://reptile-database.reptarium.cz/species?genus=Boiruna&species=maculata&search_param=%28%28taxon%3D%27snake%27%29%28reference%3D%27Rio+Grande+do+Sul%27%29%29",
            "https://reptile-database.reptarium.cz/species?genus=Bothrops&species=alternatus&search_param=%28%28taxon%3D%27snake%27%29%28reference%3D%27Rio+Grande+do+Sul%27%29%29",
            "https://reptile-database.reptarium.cz/species?genus=Bothrops&species=cotiara&search_param=%28%28taxon%3D%27snake%27%29%28reference%3D%27Rio+Grande+do+Sul%27%29%29",
            "https://reptile-database.reptarium.cz/species?genus=Bothrops&species=jararaca&search_param=%28%28taxon%3D%27snake%27%29%28reference%3D%27Rio+Grande+do+Sul%27%29%29",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Parse the query parameters from the URL
        query_params = parse_qs(urlparse(response.url).query)

        # Extract genus and species names from query parameters
        genus = query_params.get("genus", [""])[0]
        species = query_params.get("species", [""])[0]

        # If genus or species is not present, log a warning and return
        if not genus or not species:
            self.log(f"Genus or species not found in URL: {response.url}")
            return

        # Construct filename with genus and species names
        filename = f"{genus}_{species}.html"

        # Write the response body to the file
        Path(filename).write_bytes(response.body)

        # Log the saved file
        self.log(f"Saved file {filename}")
