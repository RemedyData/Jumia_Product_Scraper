import scrapy
from bs_extractor.extractors import extract_product_details

class JumiaSkinCareSpider(scrapy.Spider):
    name = "jumia_skin_care"
    allowed_domains = ["jumia.com.ng"]

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 16,
        'RETRY_TIMES': 3,
        'FEED_EXPORT_ENCODING': 'utf-8',
        'LOG_LEVEL': 'INFO',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 3.0,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 8.0,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_count = 0

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.jumia.com.ng/skin-care-prducts/?page=1",
            callback=self.parse_listing
        )


    def parse_listing(self, response):
        # Extract product links from category page
        product_links = response.css("a.core::attr(href)").getall()
        for href in product_links:
            full_url = response.urljoin(href)
            yield scrapy.Request(url=full_url, callback=self.parse_product)

        # Handle pagination
        next_page = response.css("a.pg::attr(href)").get()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse_listing)

    def parse_product(self, response):
        product_data = extract_product_details(response.text, response.url)
        if product_data:
            self.product_count += 1
            if self.product_count % 50 == 0:
                self.logger.info(f"Scraped {self.product_count} skin-care products so far")
            yield product_data

    def closed(self, reason):
        self.logger.info(f"Finished scraping {self.product_count} skin-care products. Reason: {reason}")
