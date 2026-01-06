import scrapy
from bs_extractor.extractors import extract_product_details

class JumiaSitemapSpider(scrapy.Spider):
    name = "jumia_sitemap"
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
            url="https://www.jumia.com.ng/slp/nc/sitemap/sitemap.xml",
            callback=self.parse_index_sitemap
        )

    def parse_index_sitemap(self, response):
        child_sitemaps = response.xpath("//*[local-name()='loc']/text()").getall()
        self.logger.info(f"Found {len(child_sitemaps)} child sitemaps")
        for sitemap in child_sitemaps:
            if sitemap.endswith(".xml"):
                yield scrapy.Request(url=sitemap, callback=self.parse_sitemap)

    def parse_sitemap(self, response):
        product_links = response.xpath("//*[local-name()='loc']/text()").getall()
        self.logger.info(f"Found {len(product_links)} product links in {response.url}")

        keywords = [
            "skin-care", "skincare", "beauty", "health-beauty",
            "face", "body", "lotion", "cream", "serum", "oil", "cleanser"
        ]

        for href in product_links:
            if "jumia.com.ng" in href and not href.endswith(".xml"):
                if any(kw in href for kw in keywords):
                    # Instead of yielding the link, request the product page
                    yield scrapy.Request(url=href, callback=self.parse_product)

    def parse_product(self, response):
        product_data = extract_product_details(response.text, response.url)
        if product_data:
            self.product_count += 1
            if self.product_count % 50 == 0:
                self.logger.info(f"Scraped {self.product_count} beauty/skin-care products so far")
            yield product_data

    def closed(self, reason):
        self.logger.info(f"Finished scraping {self.product_count} beauty/skin-care products. Reason: {reason}")
