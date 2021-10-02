import requests
import time
from bs4 import BeautifulSoup

site_url = "https://gatry.com/"
offers = []
keywords = []


def run_sale_monitor():
    while True:
        page = requests.get(site_url)
        parsed_page = BeautifulSoup(page.content, "html.parser")
        promos = parsed_page.find_all(class_="promocao")

        for promo in promos:
            info = promo.find(class_="informacoes")

            name_tag = info.find("h3", itemprop="name").find("a")
            product_name = name_tag.text

            if not next(
                (kw for kw in keywords if kw.lower() in product_name.lower()), None
            ):
                continue

            sale_id = promo.get("id").replace("promocao-", "")

            if next((offer for offer in offers if sale_id == offer["sale_id"]), None):
                continue

            sale = {
                "sale_id": int(sale_id),
                "product_name": product_name,
                "product_image_url": name_tag["href"],
                "product_price": info.find("span", itemprop="price").text,
                "sale_url": info.find(class_="link_loja")["href"],
                "aggregator_url": info.find(class_="mais")["href"],
                "sale_date": info.find(class_="data_postado")["title"].replace(
                    " às ", " "
                ),
            }

        # post_date_obj = datetime.strptime(post_date, "%d/%m/%Y %H:%M")

        # print(json.dumps(offers, indent=4, sort_keys=True, ensure_ascii=False))
        # print("total: " + str(len(offers)))
        time.sleep(60)
