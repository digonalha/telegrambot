import requests
import time
from datetime import datetime, date
from bs4 import BeautifulSoup
from sqlalchemy.sql.functions import user
from src.services import (
    message_service,
    tracked_sale_service,
    keyword_service,
)


def run_sale_tracker() -> None:
    site_url = "https://gatry.com"
    today = date.today()

    """Loop for sale's tracker sites web scraping."""
    while True:
        if len(keyword_service.keywords) == 0:
            time.sleep(30)
            continue

        if today != date.today():
            tracked_sale_service.get_all_tracked_sales()
            today = date.today()

        page = requests.get(site_url)
        parsed_page = BeautifulSoup(page.content, "html.parser")
        promos = parsed_page.find_all(class_="promocao")

        for promo in promos:
            info = promo.find(class_="informacoes")
            imagem = promo.find(class_="imagem")
            sale_id = int(promo.get("id").replace("promocao-", ""))

            if next(
                (
                    ts
                    for ts in tracked_sale_service.tracked_sales
                    if sale_id == ts.sale_id
                ),
                None,
            ):
                continue

            name_tag = info.find("h3", itemprop="name").find("a")
            product_name = name_tag.text

            users_keyword_to_answer = []
            lower_product_name = product_name.lower()

            for keyword in keyword_service.keywords:
                lower_keywords = keyword.keyword.lower().split()
                if all(k in lower_product_name for k in lower_keywords):
                    users_keyword_to_answer.append(keyword)

            if not users_keyword_to_answer or len(users_keyword_to_answer) == 0:
                continue

            sale = {
                "sale_id": sale_id,
                "product_name": product_name,
                "product_image_url": imagem.find("img")["src"],
                "price": "R$ " + info.find("span", itemprop="price").text,
                "sale_url": info.find(class_="link_loja")["href"],
                "aggregator_url": site_url + info.find(class_="mais")["href"],
                "sale_date": datetime.strptime(
                    info.find(class_="data_postado")["title"].replace(" às ", " "),
                    "%d/%m/%Y %H:%M",
                ),
                "created_on": datetime.now(),
            }

            db_tracked_sale = tracked_sale_service.add_tracked_sale_if_not_exists(sale)

            if not db_tracked_sale:
                continue

            messages_to_send = []

            for user_keyword in users_keyword_to_answer:
                message_with_same_chat_id = next(
                    (
                        m
                        for m in messages_to_send
                        if m["user_id"] == user_keyword.user_id
                    ),
                    None,
                )

                if not message_with_same_chat_id:
                    new_message = {
                        "user_id": user_keyword.user_id,
                        "text": (
                            f"*{db_tracked_sale.product_name}*\n"
                            f"Valor: {db_tracked_sale.price}\n\n"
                            f"[Link promoção]({db_tracked_sale.sale_url}) - [Link Gatry]({db_tracked_sale.aggregator_url})\n\n"
                        ),
                    }

                    messages_to_send.append(new_message)

            for message in messages_to_send:
                message_service.send_image(
                    message["user_id"],
                    db_tracked_sale.product_image_url,
                    message["text"],
                )

        time.sleep(60)
