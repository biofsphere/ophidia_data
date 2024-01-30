from urllib.parse import urljoin

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

            # Construct the target URL based on the extracted information
            target_url = urljoin(response.url, link_element.xpath("./@href").get())

            # Yield a request for each target URL
            yield scrapy.Request(url=target_url, callback=self.parse)

    def parse(self, response):
        # Extract genus and species names from the target URL
        genus = response.url.split("&genus=")[1].split("&")[0]
        species = response.url.split("&species=")[1].split("&")[0]

        # Construct filename with genus and species names
        filename = f"{genus}_{species}.html"

        # Write the response body to the file
        with open(filename, "wb") as file:
            file.write(response.body)

        # Log the saved file
        self.log(f"Saved file {filename}")
