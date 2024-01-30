from urllib.parse import parse_qs, urljoin, urlparse

import scrapy


class SnakesImgSpider(scrapy.Spider):
    name = "snakesimg"

    def start_requests(self):
        # Start by making a request to the main URL containing the links
        main_url = "https://reptile-database.reptarium.cz/advanced_search?taxon=snake&reference=Rio+Grande+do+Sul&submit=Search"
        yield scrapy.Request(url=main_url, callback=self.parse_links)

    def parse_links(self, response):
        # Extract the links from the specified XPath
        link_elements = response.xpath('//*[@id="content"]/ul[2]/li/a')

        # Iterate through the link elements to generate the target URLs
        for link_element in link_elements:
            # Extract genus and species names from the link text
            genus_species = link_element.xpath("./text()").get()

            # If genus_species is not present, log a warning and continue to the next link
            if not genus_species:
                self.log(
                    f"Genus and species not found in link: {link_element.extract()}"
                )
                continue

            # Construct the target URL based on the extracted information
            target_url = urljoin(response.url, link_element.xpath("./@href").get())

            # Yield a request for each target URL
            yield scrapy.Request(url=target_url, callback=self.parse_species_page)

    def parse_species_page(self, response):
        # Extract genus and species names from the target URL
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url.query)
        genus = query_params.get("genus", [""])[0]
        species = query_params.get("species", [""])[0]

        # If genus or species is not present, log a warning and return
        if not genus or not species:
            self.log(f"Genus or species not found in URL: {response.url}")
            return

        # Construct filename with genus and species names
        filename = f"{genus}_{species}.html"

        # Write the response body to the file
        with open(filename, "wb") as file:
            file.write(response.body)

        # Log the saved file
        self.log(f"Saved file {filename}")
