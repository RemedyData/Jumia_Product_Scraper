# Jumia Web Scraping Project

This project scrapes product data from [Jumia Nigeria](https://www.jumia.com.ng) using **Scrapy** and processes it with **pandas** for analysis.

## Features
- Scrapes multiple categories: Skin Care, Beauty Styling, Health & Beauty, Personal Care.
- Extracts product details: name, brand, price, discount, rating, reviews, description, ingredients.
- Handles pagination across 50 pages per category.
- Saves separate CSVs per category and one master dataset.
- Deduplicates products across categories.
- Generates summary statistics with pandas.

## Repository Structure
- `scrapy_spider/` → Scrapy spiders
- `bs_extractor/` → Product detail extraction logic
- `output/` → Scraped datasets
- `scripts/` → Post-processing scripts
- `requirements.txt` → Dependencies
- `README.md` → Documentation

## Challenges & Remedies
- **Sitemap issues** → Switched to category pagination.
- **Duplicates across categories** → Added category tagging + deduplication.
- **Network hiccups** → Increased retries & enabled job persistence.
- **Scrapy deprecation** → Updated spider to use `start()` instead of `start_requests()`.

## Dataset Schema
| Field                 | Description |
|------------------------|-------------|
| product_url           | Full URL of product detail page |
| product_name          | Name of the product |
| brand_name            | Brand |
| final_price           | Price after discount |
| discount_made         | Discount percentage |
| size                  | Size/variant |
| rating                | Average rating |
| num_reviews           | Number of reviews |
| category_product_type | Product description / type |
| ingredient_name       | Ingredients (if available) |
| category              | Source category (skin-care, beauty-styling, health-beauty, personal-care) |

## Requirements
- scrapy==2.13.3
- pandas==2.2.2
- numpy==2.0.0
- lxml==6.0.2


**Install with**:
```bash
pip install -r requirements.txt
```

▶️ **Usage**

**Run spider**:
```bash
scrapy runspider scrapy_spider/jumia_beauty_spider.py -s JOBDIR=crawls/jumia
```

**Merge datasets**:
```bash
python scripts/merge_jumia.py
```

**Generate summary stats**:
```bash
python scripts/summary_stats.py
```

## 📊 Example Output
- output/jumia_beauty_master.csv → ~16,000 rows (all products, duplicates included).

- output/jumia_beauty_unique.csv → ~7,000–8,000 unique products.

## 🔗 Links
- Jumia Nigeria: https://www.jumia.com.ng

- Scrapy Docs: https://docs.scrapy.org

- Pandas Docs: https://pandas.pydata.org

## 🏷️ Hashtags
- #WebScraping #Python #Scrapy #DataEngineering #ETL #DataScience #Automation









