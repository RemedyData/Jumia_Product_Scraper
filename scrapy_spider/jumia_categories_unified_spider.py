import scrapy
from bs_extractor.extractors import extract_product_details

class JumiaCategoriesUnifiedSpider(scrapy.Spider):
    name = "jumia_categories_unified"
    allowed_domains = ["jumia.com.ng"]

    # Start from category listing; pagination will discover more pages
    start_urls = [
        "https://www.jumia.com.ng/skin-care-prducts/?page=1",
        # You can add more categories here if needed
        # "https://www.jumia.com.ng/beauty-styling-products/?page=1",
        # "https://www.jumia.com.ng/health-beauty/?page=1",
    ]

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

    def __init__(self, limit=20, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit = int(limit)
        self.product_count = 0
        self.seen_urls = set()

    def parse(self, response):
        # 1) Extract product card links from the category grid
        product_hrefs = response.css("a.core::attr(href)").getall()
        self.logger.info(f"Found {len(product_hrefs)} product card links on {response.url}")

        for href in product_hrefs:
            full_url = response.urljoin(href)
            # Only follow real product detail pages that end with .html
            if full_url.endswith(".html") and full_url not in self.seen_urls:
                if self.limit and self.product_count >= self.limit:
                    return
                self.seen_urls.add(full_url)
                self.logger.info(f"Queueing product page: {full_url}")
                yield scrapy.Request(url=full_url, callback=self.parse_product)

        # 2) Follow pagination (next page)
        next_page = response.css("a.pg::attr(href)").get()
        if next_page and (not self.limit or self.product_count < self.limit):
            next_url = response.urljoin(next_page)
            self.logger.info(f"Following pagination to: {next_url}")
            yield scrapy.Request(url=next_url, callback=self.parse)

    def parse_product(self, response):
        if self.limit and self.product_count >= self.limit:
            return

        # Use your working extractor that produced full fields before
        product_data = extract_product_details(response.text, response.url)
        if product_data:
            self.product_count += 1
            self.logger.info(f"[{self.product_count}] Extracted: {response.url}")
            yield product_data
        else:
            # If extractor returns nothing, log and continue
            self.logger.info(f"Extractor returned empty for: {response.url}")

    def closed(self, reason):
        self.logger.info(f"Finished scraping {self.product_count} products. Reason: {reason}")
