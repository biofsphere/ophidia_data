import os
import scrapy
from urllib.parse import urljoin, urlparse, parse_qs
from scrapy.pipelines.images import ImagesPipeline

class SnakesImgSpider(scrapy.Spider):
    name = "snakesimg"

    # Use the full path for IMAGES_STORE
    custom_settings = {
        'ITEM_PIPELINES': {'scrapy.pipelines.images.ImagesPipeline': 1},
        'IMAGES_STORE': os.path.abspath('images'),  # Set the folder to store downloaded images
        'IMAGES_EXPIRES': 90,  # Set the expiration time for cached images (days)
        'LOG_LEVEL': 'DEBUG',  # Set the log level to DEBUG for more detailed output
    }

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
            genus_species = link_element.xpath('./text()').get()

            # If genus_species is not present, log a warning and continue to the next link
            if not genus_species:
                self.log(f"Genus and species not found in link: {link_element.extract()}")
                continue

            # Construct the target URL based on the extracted information
            target_url = urljoin(response.url, link_element.xpath('./@href').get())

            # Yield a request for each target URL
            yield scrapy.Request(url=target_url, callback=self.parse_species_page, meta={'genus_species': genus_species})

    def parse_species_page(self, response):
        # Extract genus and species names from the target URL
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url.query)
        genus = query_params.get('genus', [''])[0]
        species = query_params.get('species', [''])[0]

        # If genus or species is not present, log a warning and return
        if not genus or not species:
            self.log(f"Genus or species not found in URL: {response.url}")
            return

        # Extract image URLs from the page
        image_urls = response.xpath('//*[@id="gallery"]//img/@src').extract()

        # Yield the image URLs for download
        for i, image_url in enumerate(image_urls, start=1):
            yield {
                'url': image_url,
                'genus_species': f"{genus}_{species}",
                'image_filename': f"{genus}_{species}_{i:03}.jpg",  # Use jpg or the appropriate image extension
            }

    def get_media_requests(self, item, info):
        for image_url in item['url']:
            yield scrapy.Request(urljoin(info.spider.base_url, image_url), meta={'item': item})

    def file_path(self, request, response=None, info=None):
        return request.meta['item']['image_filename']
