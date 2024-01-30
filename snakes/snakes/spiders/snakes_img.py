import scrapy
from scrapy.http import FormRequest
from urllib.parse import urljoin

class SpeciesItem(scrapy.Item):
    genus = scrapy.Field()
    species = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()

class SnakesImgSpider(scrapy.Spider):
    name = "snakesimg"

    def start_requests(self):
        yield FormRequest(
            url="https://reptile-database.reptarium.cz/advanced_search?taxon=snake&reference=Rio+Grande+do+Sul&submit=Search",
            callback=self.parse_links,
        )

    def parse_links(self, response):
        link_elements = response.xpath('//*[@id="content"]/ul[2]/li/a')

        for link_element in link_elements:
            genus_species = link_element.xpath("./text()").get()
            target_url = urljoin(response.url, link_element.xpath("./@href").get())

            yield scrapy.Request(
                url=target_url,
                callback=self.parse_species_page,
                meta={"genus": genus_species},
            )

    def parse_species_page(self, response):
        genus = response.meta["genus"]

        # Extract image URLs and store them in an item field called 'image_urls'
        image_urls = response.xpath('//div[@id="gallery"]//img/@src').getall()

        # Convert relative URLs to absolute URLs
        image_urls = [urljoin(response.url, url.strip()) for url in image_urls if url.strip()]

        item = SpeciesItem()
        item["genus"] = genus
        item["species"] = response.xpath('//h1[@class="species"]/text()').get()
        item["image_urls"] = image_urls

        yield item