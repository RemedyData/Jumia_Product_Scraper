from bs4 import BeautifulSoup

def extract_product_details(html, url):
    soup = BeautifulSoup(html, "lxml")

    def get_text(selector):
        el = soup.select_one(selector)
        return el.get_text(strip=True) if el else None
    

    def get_ingredient_block():
        for p in soup.select("p"):
            if "INGREDIENT" in p.get_text(strip=True).upper():
                next_p = p.find_next_sibling("p")
                return next_p.get_text(strip=True) if next_p else None
        return None
    
    
    def get_brand_name():
        for div in soup.select("div.-pvxs"):
            if "Brand:" in div.get_text():
                first_link = div.find("a")
                return first_link.get_text(strip=True) if first_link else None
        return None
    

    return {
        "product_url": url,
        "product_name": get_text("h1.-fs20.-pts.-pbxs"),
        "brand_name": get_brand_name(),
        "final_price": get_text("div.prc") or get_text("span.-b.-ubpt"),
        "discount_made": get_text("div.s-prc-w .bdg._dsct") or get_text("span.bdg._dsct"),
        "size": get_text("h1.-fs20.-pts.-pbxs"),
        "rating": get_text("div.-fs29 span.-b"),
        "num_reviews": get_text("p.-fs16.-pts"),
        "category_product_type": " ".join(p.get_text(strip=True) for p in soup.select("div.markup p")[:2]),
        "ingredient_name": get_ingredient_block(),
    }
