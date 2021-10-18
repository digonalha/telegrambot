import requests
import json
from time import sleep
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from random import randint

from src.services import (
    message_service,
    tracked_sale_service,
    keyword_service,
)
from src.api import promobit_api
from src.helpers import string_helper


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
        return str_more_info
    except:
        return ""


def check_promobit_sales() -> bool:
    promobit_sales = promobit_api.get_last_sales(100)

    if not promobit_sales or len(promobit_sales) == 0:
        return False

    for psale in promobit_sales:
        sale_date = datetime.strptime(
            psale["offer_published"], "%Y-%m-%dT%H:%M:%S%z"
        ).replace(tzinfo=None)

        greater_than_date = datetime.now() - timedelta(1)

        if sale_date <= greater_than_date:
            return

        users_keyword_to_answer = []
        lower_product_name = psale["offer_title"].lower()

        for keyword in keyword_service.keywords:
            lower_keywords = keyword.keyword.lower().split()
            if all(k in lower_product_name for k in lower_keywords):
                users_keyword_to_answer.append(keyword)

        if not users_keyword_to_answer or len(users_keyword_to_answer) == 0:
            continue

        price = "R${:,.2f}".format(psale["offer_price"])
        main_currency, fractional_currency = price.split(".")[0], price.split(".")[1]
        new_main_currency = main_currency.replace(",", ".")
        price = new_main_currency + "," + fractional_currency

        old_price = ""

        if psale["offer_old_price"] != 0:
            psale["offer_old_price"]
            old_price = (
                f'<s>{string_helper.format_currency(psale["offer_old_price"])}</s>  '
            )

        old_new_price = (
            f'{old_price}{string_helper.format_currency(psale["offer_price"])}'
        )

        sale = {
            "sale_id": psale["offer_id"],
            "product_name": psale["offer_title"],
            "product_image_url": f"https://i.promobit.com.br/268{psale['offer_photo']}",
            "price": old_new_price,
            "sale_url": f"https://www.promobit.com.br/Redirect/to/{psale['offer_id']}",
            "aggregator_url": f"https://www.promobit.com.br/oferta/{psale['offer_slug']}",
            "sale_date": sale_date,
            "created_on": datetime.now(),
        }

        db_tracked_sale = tracked_sale_service.add_tracked_sale_if_not_exists(sale)

        if not db_tracked_sale:
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
                        f"<b>{db_tracked_sale.product_name}</b>\n\n"
                        f"<b>Valor: {db_tracked_sale.price}</b>\n"
                        f"<b>Data: {sale['sale_date'].strftime('%d/%m - %H:%M')}</b>\n\n"
                        f"{get_promobit_sale_info(db_tracked_sale.aggregator_url)}"
                        f"<i>Vendido por {psale['store_name']}</i>"
                    ),
                }
                messages_to_send.append(new_message)

        reply_markup = (
            '{"inline_keyboard": [[{"text":"Ir para promoção", "url": "'
            + db_tracked_sale.sale_url
            + '"}],[{"text":"Ver oferta no Promobit", "url": "'
            + db_tracked_sale.aggregator_url
            + '"}]]}'
        )

        for message in messages_to_send:
            message_service.send_image(
                message["user_id"],
                db_tracked_sale.product_image_url,
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
            (ts for ts in tracked_sale_service.tracked_sales if sale_id == ts.sale_id),
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
            "price": "R$" + info.find("span", itemprop="price").text,
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
                        f"*{db_tracked_sale.product_name}*\n\n"
                        f"*Valor: {db_tracked_sale.price}*\n"
                        f"*Data: {sale['sale_date'].strftime('%d/%m -  %H:%M')}*\n\n"
                        f"_Vendido por {store_name}_"
                    ),
                }
                messages_to_send.append(new_message)

        reply_markup = (
            '{"inline_keyboard": [[{"text":"Ir para promoção", "url": "'
            + db_tracked_sale.sale_url
            + '"}],[{"text":"Ver oferta no Gatry", "url": "'
            + db_tracked_sale.aggregator_url
            + '"}]]}'
        )

        for message in messages_to_send:
            message_service.send_image(
                message["user_id"],
                db_tracked_sale.product_image_url,
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
            tracked_sale_service.get_all_tracked_sales()
            today = date.today()

        check_gatry_sales()
        check_promobit_sales()

        # if not request_success:
        # sleep(randint(62, 124))

        sleep(randint(62, 126))
