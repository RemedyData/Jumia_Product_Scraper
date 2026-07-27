import scrapy

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

    def __init__(self, limit=20, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.limit = int(limit)
        self.product_count = 0

    def start_requests(self):
        # Jumia sitemap index
        yield scrapy.Request(
            url="https://www.jumia.com.ng/sitemap.xml",
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
            # Only follow real product pages (ending in .html)
            if href.endswith(".html") and any(kw in href for kw in keywords):
                yield scrapy.Request(url=href, callback=self.parse_product)

    def parse_product(self, response):
        if self.product_count >= self.limit:
            return

        product_data = {
            "product_url": response.url,
            "product_name": response.css("h1::text").get(),
            "brand_name": response.css("a.-b.-ub::text").get(),
            "final_price": response.css("span.-b::text").get(),
            "old_price": response.css("span.-s::text").get(),
            "rating": response.css("div.stars::attr(data-rating)").get(),
            "num_reviews": response.css("p.rev::text").get(),
            "category": " > ".join(response.css("ul.breadcrumb li a::text").getall()),
        }

        self.product_count += 1
        self.logger.info(f"Extracted fields for {response.url}: {product_data}")
        yield product_data


    def closed(self, reason):
        self.logger.info(f"Finished scraping {self.product_count} beauty/skin-care products. Reason: {reason}")
