import requests
import json
import math
from time import sleep
from datetime import datetime, date, timedelta, timezone
from bs4 import BeautifulSoup
from random import randint

from services import (
    message_service,
    sale_service,
    keyword_service,
)
from api import promobit_api
from helpers import string_helper


def get_promobit_sale_info(aggregator_url: str) -> str:
    try:
        page = requests.get(aggregator_url)
        parsed_page = BeautifulSoup(page.content, "html.parser")

        scripts_result = parsed_page.find("script", id="__NEXT_DATA__").text
        js = json.loads(scripts_result)

        more_info = js["props"]["pageProps"]["offer"]["offerInstructions"]
        more_info = string_helper.html_sanitize(more_info)

        if more_info:
            return f"<u>Informações adicionais</u>\n{more_info}\n\n"

        return ""
    except:
        return ""


def check_promobit_sales() -> bool:
    promobit_sales = promobit_api.get_last_sales(100)

    if not promobit_sales or len(promobit_sales) == 0:
        return False

    for psale in promobit_sales:
        sale_date = datetime.strptime(
            psale["offer_published"], "%Y-%m-%dT%H:%M:%S%z"
        ).replace(tzinfo=timezone.utc)

        greater_than_date = datetime.now() - timedelta(days=1)
        greater_than_date = greater_than_date.replace(tzinfo=timezone.utc)

        if sale_date <= greater_than_date:
            return

        sale = {
            "sale_id": psale["offer_id"],
            "product_name": psale["offer_title"].strip(),
            "product_image_url": f"https://i.promobit.com.br/268{psale['offer_photo']}",
            "old_price": psale["offer_old_price"],
            "price": psale["offer_price"],
            "sale_url": f"https://www.promobit.com.br/Redirect/to/{psale['offer_id']}",
            "aggregator_url": f"https://www.promobit.com.br/oferta/{psale['offer_slug']}",
            "sale_date": sale_date,
            "created_on": datetime.now(),
        }

        db_sale = sale_service.add_sale_if_not_exists(sale)

        if not db_sale:
            return

        users_keyword_to_answer = []
        lower_product_name = psale["offer_title"].lower()

        for keyword in keyword_service.keywords:
            lower_keywords = keyword.keyword.lower().split()
            if all(k in lower_product_name for k in lower_keywords):
                if keyword.max_price and keyword.max_price < math.trunc(
                    psale["offer_price"]
                ):
                    continue

                users_keyword_to_answer.append(keyword)

        if not users_keyword_to_answer or len(users_keyword_to_answer) == 0:
            continue

        messages_to_send = []
        for user_keyword in users_keyword_to_answer:
            message_with_same_chat_id = next(
                (m for m in messages_to_send if m["user_id"] == user_keyword.user_id),
                None,
            )
            if not message_with_same_chat_id:
                new_message = {
                    "user_id": user_keyword.user_id,
                    "text": (
                        f"<b>{db_sale.product_name}</b>\n\n"
                        f"<b>Valor: {string_helper.get_old_new_price_str(db_sale.price, db_sale.old_price)}</b>\n"
                        f"<b>Data: {sale['sale_date'].strftime('%d/%m - %H:%M')}</b>\n\n"
                        f"{get_promobit_sale_info(db_sale.aggregator_url)}"
                        f"<i>Vendido por {psale['store_name'] if psale['store_name'] else psale['store_domain']}</i>"
                    ),
                }
                messages_to_send.append(new_message)

        reply_markup = (
            '{"inline_keyboard": [[{"text":"Ir para promoção", "url": "'
            + db_sale.sale_url
            + '"}],[{"text":"Ver oferta no Promobit", "url": "'
            + db_sale.aggregator_url
            + '"}]]}'
        )

        for message in messages_to_send:
            message_service.send_image(
                message["user_id"],
                db_sale.product_image_url,
                message["text"],
                reply_markup,
                parse_mode="HTML",
            )

    return True


def check_gatry_sales():
    site_url = "https://gatry.com"
    page = requests.get(site_url)
    parsed_page = BeautifulSoup(page.content, "html.parser")
    promos = parsed_page.find_all(class_="promocao")
    for promo in promos:
        info = promo.find(class_="informacoes")
        imagem = promo.find(class_="imagem")
        sale_id = int(promo.get("id").replace("promocao-", ""))
        if next(
            (ts for ts in sale_service.sales if sale_id == ts.sale_id),
            None,
        ):
            continue
        name_tag = info.find("h3", itemprop="name").find("a")
        product_name = name_tag.text
        users_keyword_to_answer = []
        lower_product_name = product_name.lower()

        sale_price = None

        try:
            sale_price = info.find("span", itemprop="price").text
            sale_price = sale_price.replace(".", "")
            sale_price = sale_price.replace(",", ".")
            sale_price = float(sale_price)
        except:
            continue

        sale_date = datetime.strptime(
            info.find(class_="data_postado")["title"].replace(" às ", " "),
            "%d/%m/%Y %H:%M",
        )

        sale_date = sale_date.replace(tzinfo=timezone.utc)

        if sale_date > datetime.now().replace(tzinfo=timezone.utc):
            sale_date = sale_date - timedelta(hours=1)

        sale = {
            "sale_id": sale_id,
            "product_name": product_name.strip(),
            "product_image_url": imagem.find("img")["src"],
            "price": sale_price,
            "sale_url": info.find(class_="link_loja")["href"],
            "aggregator_url": site_url + info.find(class_="mais")["href"],
            "sale_date": sale_date,
            "created_on": datetime.now(),
        }
        db_sale = sale_service.add_sale_if_not_exists(sale)

        if not db_sale:
            return

        for keyword in keyword_service.keywords:
            lower_keywords = keyword.keyword.lower().split()
            if all(k in lower_product_name for k in lower_keywords):
                if keyword.max_price and keyword.max_price < math.trunc(sale_price):
                    continue
                users_keyword_to_answer.append(keyword)

        if not users_keyword_to_answer or len(users_keyword_to_answer) == 0:
            continue

        store_name = info.find(class_="link_loja").text

        if store_name:
            try:
                store_name = store_name.split("Ir para ")[1]
            except:
                store_name = "Não informado"

        messages_to_send = []
        for user_keyword in users_keyword_to_answer:
            message_with_same_chat_id = next(
                (m for m in messages_to_send if m["user_id"] == user_keyword.user_id),
                None,
            )
            if not message_with_same_chat_id:
                new_message = {
                    "user_id": user_keyword.user_id,
                    "text": (
                        f"*{db_sale.product_name}*\n\n"
                        f"*Valor: {string_helper.get_old_new_price_str(db_sale.price)}*\n"
                        f"*Data: {sale['sale_date'].strftime('%d/%m - %H:%M')}*\n\n"
                        f"_Vendido por {store_name}_"
                    ),
                }
                messages_to_send.append(new_message)

        reply_markup = (
            '{"inline_keyboard": [[{"text":"Ir para promoção", "url": "'
            + db_sale.sale_url
            + '"}],[{"text":"Ver oferta no Gatry", "url": "'
            + db_sale.aggregator_url
            + '"}]]}'
        )

        for message in messages_to_send:
            message_service.send_image(
                message["user_id"],
                db_sale.product_image_url,
                message["text"],
                reply_markup,
            )


def run_sale_tracker() -> None:
    today = date.today()

    """Loop for sale's tracker sites web scraping."""
    while True:
        if len(keyword_service.keywords) == 0:
            sleep(120)
            continue

        if today != date.today():
            sale_service.get_last_day_sales()
            today = date.today()

        check_gatry_sales()
        check_promobit_sales()

        # if not request_success:
        # sleep(randint(62, 124))

        sleep(randint(62, 126))
