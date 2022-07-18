import requests
import json
import math
from time import sleep
from datetime import datetime, date, timedelta, timezone
from bs4 import BeautifulSoup
from random import randint

from app.configs import settings
from app.api import promobit_api
from domain.services import message_service
from shared.helpers.logging_helper import SystemLogging
from shared.helpers import string_helper
from domain.models.sale import Sale
from domain.services import (
    sale_service,
    keyword_service,
)

syslog = SystemLogging(__name__)


def get_promobit_sale_info(aggregator_url: str) -> str:
    try:
        page = requests.get(aggregator_url)
        parsed_page = BeautifulSoup(page.content, "html.parser")

        scripts_result = parsed_page.find("script", id="__NEXT_DATA__").text
        js = json.loads(scripts_result)

        more_info = js["props"]["pageProps"]["offer"]["offerInstructions"]
        more_info = string_helper.html_sanitize(more_info)

        if more_info:
            return f"<u>Informações adicionais</u>\n{more_info}"

        return ""
    except:
        return ""


def send_user_message(
    sale: Sale, aggregator_name: str, description: str = None
) -> bool:
    users_keyword_to_answer = []
    lower_product_name = sale.product_name.lower()

    for keyword in keyword_service.keywords:
        lower_keyword = keyword.keyword.lower()
        split_keyword = lower_keyword.split()
        if all(k in lower_product_name for k in split_keyword):
            if keyword.max_price and keyword.max_price < math.trunc(sale.price):
                continue
            users_keyword_to_answer.append(keyword)

    if not users_keyword_to_answer or len(users_keyword_to_answer) == 0:
        return False

    messages_to_send = []

    sale_description = description

    if aggregator_name == "Promobit":
        sale_description = get_promobit_sale_info(sale.aggregator_url)

    if sale_description:
        sale_description = "\n\n" + sale_description

    for user_keyword in users_keyword_to_answer:
        message_with_same_chat_id = next(
            (m for m in messages_to_send if m["user_id"] == user_keyword.user_id),
            None,
        )

        if not message_with_same_chat_id:
            new_message = {
                "user_id": user_keyword.user_id,
                "keywords": user_keyword.keyword,
                "text": (
                    f"<b>{string_helper.html_sanitize(sale.product_name)}</b>\n\n"
                    f"<b>Valor: {string_helper.get_old_new_price_str(sale.price, sale.old_price)}</b>\n"
                    f"<b>Data: {sale.sale_date.strftime('%d/%m - %H:%M')}</b>"
                    f"{('' if not sale_description else sale_description)}"
                ),
            }
            messages_to_send.append(new_message)
        elif message_with_same_chat_id["keywords"] != user_keyword.keyword:
            for msg in messages_to_send:
                if msg["user_id"] == message_with_same_chat_id["user_id"]:
                    msg["keywords"] = msg["keywords"] + ";" + user_keyword.keyword

    for message in messages_to_send:
        reply_markup = (
            '{"inline_keyboard": [[{"text":"Ir para promoção ('
            + string_helper.html_sanitize(sale.store_name)
            + ')", "url": "'
            + sale.sale_url
            + '"}],[{"text":"Ver no '
            + aggregator_name
            + '", "url": "'
            + sale.aggregator_url
            + '"},'
            + '{"text": "Parar de monitorar", "callback_data": '
            + '"delkeywords|'
            + message["keywords"]
            + '"}]]}'
        )
        text = (
            message["text"]
            + "\n\n<b>Palavra-chave:</b> <i>"
            + message["keywords"].replace(";", ", ")
            + "</i>"
        )
        message_service.send_image(
            message["user_id"],
            sale.product_image_url,
            text,
            reply_markup,
            parse_mode="HTML",
        )


def send_channel_message(
    sale: Sale, aggregator_name: str, description: str = None
) -> None:
    sale_description = description

    if aggregator_name == "Promobit":
        sale_description = get_promobit_sale_info(sale.aggregator_url)

    if sale_description:
        sale_description = "\n\n" + sale_description

    new_message = (
        f"<b>{string_helper.html_sanitize(sale.product_name)}</b>\n\n"
        f"<b>Valor: {string_helper.get_old_new_price_str(sale.price, sale.old_price)}</b>\n"
        f"<b>Data: {sale.sale_date.strftime('%d/%m - %H:%M')}</b>"
        f"{('' if not sale_description else sale_description)}"
    )

    reply_markup = (
        '{"inline_keyboard": [[{"text":"Ir para promoção ('
        + string_helper.html_sanitize(sale.store_name)
        + ')", "url": "'
        + sale.sale_url
        + '"}],[{"text":"Ver oferta no '
        + aggregator_name
        + '", "url": "'
        + sale.aggregator_url
        + '"}]]}'
    )

    message_service.send_image(
        settings.promobot_channel,
        sale.product_image_url,
        new_message,
        reply_markup,
        parse_mode="HTML",
    )

    sleep(1)


def check_promobit_sales() -> bool:
    promobit_sales = promobit_api.get_last_sales(50)

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

        image_url = None

        if "http" in psale["offer_photo"]:
            image_url = psale["offer_photo"]
        else:
            image_url = f"https://i.promobit.com.br/268{psale['offer_photo']}"

        sale = {
            "sale_id": psale["offer_id"],
            "product_name": psale["offer_title"].strip(),
            "product_image_url": image_url,
            "old_price": psale["offer_old_price"],
            "price": psale["offer_price"],
            "sale_url": f"https://www.promobit.com.br/Redirect/to/{psale['offer_id']}",
            "aggregator_url": f"https://www.promobit.com.br/oferta/{psale['offer_slug']}",
            "sale_date": sale_date,
            "created_on": datetime.now(),
            "store_name": psale["store_name"]
            if psale["store_name"]
            else psale["store_domain"],
        }

        db_sale = sale_service.add_sale_if_not_exists(sale)

        if not db_sale:
            return

        send_channel_message(db_sale, aggregator_name="Promobit")
        send_user_message(db_sale, aggregator_name="Promobit")


def check_gatry_sales():
    site_url = "https://gatry.com"
    page = requests.get(site_url)
    parsed_page = BeautifulSoup(page.content, "html.parser")
    promos = parsed_page.find_all("article")
    for promo in promos:
        info = promo.find(class_="description")
        imagem = promo.find(class_="image")

        agg_url = info.find(class_="option-more").find("a")["href"]
        sale_id = int(agg_url.split("/")[2])

        if next(
            (ts for ts in sale_service.sales if sale_id == ts.sale_id),
            None,
        ):
            continue

        name_tag = info.find("h3").find("a")
        product_name = name_tag.text

        sale_price = None

        try:
            sale_price = info.find(class_="price").text
            sale_price = sale_price.replace(".", "")
            sale_price = sale_price.replace(",", ".")
            sale_price = sale_price.replace("R$", "")
            sale_price = sale_price.replace("&nbsp;", "")
            sale_price = sale_price.replace(" ", "")
            sale_price = sale_price.replace("\n\xa0", "")
            sale_price = float(sale_price)
        except:
            sale_price = 0

        date_str = str(info.find(class_="date")["title"].replace(" às ", " "))

        sale_date = datetime.strptime(
            date_str.strip(),
            "%d/%m/%Y %H:%M",
        )

        sale_date = sale_date.replace(tzinfo=timezone.utc)

        if sale_date > datetime.now().replace(tzinfo=timezone.utc):
            sale_date = sale_date - timedelta(hours=1)

        store_name = info.find(class_="option-store").text

        if store_name:
            try:
                store_name = store_name.split("Ir para ")[1]
            except:
                store_name = "Não informado"

        sale = {
            "sale_id": sale_id,
            "product_name": product_name.strip(),
            "product_image_url": imagem.find("img")["src"],
            "price": sale_price,
            "sale_url": info.find(class_="option-store").find("a")["href"],
            "aggregator_url": site_url
            + info.find(class_="option-more").find("a")["href"],
            "sale_date": sale_date,
            "created_on": datetime.now(),
            "store_name": store_name.strip(),
        }
        db_sale = sale_service.add_sale_if_not_exists(sale)

        if not db_sale:
            return

        send_channel_message(db_sale, aggregator_name="Gatry")
        send_user_message(db_sale, aggregator_name="Gatry")


def check_boletando_sales():
    site_url = "https://boletando.com/"
    page = requests.get(site_url)
    parsed_page = BeautifulSoup(page.content, "html.parser")
    promos = parsed_page.find_all(class_="col_item")
    for promo in promos:
        info = promo.find(class_="info_in_dealgrid")
        imagem = info.find("figure").find("a").find("img")
        product_description = info.find("h3").find("a")
        agg_url = product_description["href"]

        if next(
            (ts for ts in sale_service.sales if agg_url == ts.aggregator_url),
            None,
        ):
            continue

        product_name = product_description.text
        sale_price = None

        try:
            sale_price = info.find(class_="rh_regular_price").text
            sale_price = sale_price.replace(".", "")
            sale_price = sale_price.replace(",", ".")
            sale_price = sale_price.replace("R$", "")
            sale_price = sale_price.replace("&nbsp;", "")
            sale_price = sale_price.replace(" ", "")
            sale_price = sale_price.replace("\n\xa0", "")
            sale_price = float(sale_price)
        except:
            sale_price = 0

        sale_date = datetime.now()
        store_name = promo.find(class_="cat_link_meta").find("a").text

        custom_notice = None
        div_custom_notice = promo.find(class_="rh_custom_notice")

        if div_custom_notice:
            custom_notice = div_custom_notice.text

        if not store_name:
            store_name = "Não informado"

        sale = {
            "sale_id": None,
            "product_name": product_name.strip(),
            "product_image_url": imagem["src"],
            "price": sale_price,
            "sale_url": promo.find(class_="rh_button_wrapper").find("a")["href"],
            "aggregator_url": agg_url,
            "sale_date": sale_date,
            "created_on": datetime.now(),
            "store_name": store_name.strip(),
        }

        db_sale = sale_service.add_sale_if_aggregator_url_not_exists(sale)

        if not db_sale:
            return

        more_info = None
        if custom_notice:
            more_info = f"<u>Informações adicionais</u>\n{string_helper.html_sanitize(custom_notice)}"

        send_channel_message(
            db_sale, aggregator_name="Boletando", description=more_info
        )
        send_user_message(db_sale, aggregator_name="Boletando", description=more_info)


def run_webscrap_worker() -> None:
    promobit_retry = 0
    gatry_retry = 0
    boletando_retry = 0
    """Loop for sale's tracker sites web scraping."""
    while True:
        try:
            sleep(randint(62, 126))

            if promobit_retry >= 0:
                try:
                    check_promobit_sales()
                except Exception as ex:
                    syslog.create_warning("webscrap_worker - promobit", ex)
                    promobit_retry += 1
            if gatry_retry >= 0:
                try:
                    check_gatry_sales()
                except Exception as ex:
                    syslog.create_warning("webscrap_worker - gatry", ex)
                    gatry_retry += 1
            if boletando_retry >= 0:
                try:
                    check_boletando_sales()
                except Exception as ex:
                    syslog.create_warning("webscrap_worker - boletando", ex)
                    boletando_retry += 1

        except Exception as ex:
            syslog.create_warning("webscrap_worker", ex)
            continue
