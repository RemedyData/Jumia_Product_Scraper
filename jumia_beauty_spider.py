import scrapy
from bs_extractor.extractors import extract_product_details

class JumiaBeautySpider(scrapy.Spider):
    name = "jumia_beauty"
    allowed_domains = ["jumia.com.ng"]

    categories = {
        "skin-care": [f"https://www.jumia.com.ng/skin-care-prducts/?page={i}" for i in range(1, 51)],
        "beauty-styling": [f"https://www.jumia.com.ng/beauty-styling-products/?page={i}" for i in range(1, 51)],
        "health-beauty": [f"https://www.jumia.com.ng/health-beauty/?page={i}" for i in range(1, 51)],
        "personal-care": [f"https://www.jumia.com.ng/slp/beauty-and-personal-care?page={i}" for i in range(1, 51)],
    }

    start_urls = sum(categories.values(), [])

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 16,
        'RETRY_TIMES': 6,
        'FEED_EXPORT_ENCODING': 'utf-8',
        'LOG_LEVEL': 'INFO',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 3.0,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 8.0,

        # Multiple feeds: one per category + one master
        'FEEDS': {
            'output/jumia_beauty_all.csv': {'format': 'csv'},
            'output/skincare.csv': {'format': 'csv', 'fields': None, 'overwrite': True},
            'output/beauty.csv': {'format': 'csv', 'fields': None, 'overwrite': True},
            'output/health.csv': {'format': 'csv', 'fields': None, 'overwrite': True},
            'output/personal.csv': {'format': 'csv', 'fields': None, 'overwrite': True},
        }
    }

    def parse(self, response):
        # Identify category from URL
        category = None
        for cat, urls in self.categories.items():
            if any(response.url.startswith(u.split("?")[0]) for u in urls):
                category = cat
                break

        product_hrefs = response.css("a.core::attr(href)").getall()
        self.logger.info(f"Found {len(product_hrefs)} product card links on {response.url} ({category})")

        for href in product_hrefs:
            full_url = response.urljoin(href)
            if full_url.endswith(".html"):
                yield scrapy.Request(url=full_url, callback=self.parse_product, meta={"category": category})

    def parse_product(self, response):
        product_data = extract_product_details(response.text, response.url)
        if product_data:
            product_data["category"] = response.meta.get("category")
            yield product_data
