import threading
import requests
import time
from bs4 import BeautifulSoup
from src.repositories.database import database
from src.services import (
    message_service,
    user_service,
    moderator_service,
    timeout_service,
    custom_command_service,
    response_service,
)

print("→ starting telegrambot")

# create tables if not exists
print("→ creating tables if not exists... ", end="")
database.create_tables()
print("done!")

# get current users on database
print("→ get all objects from tables... ", end="")
user_service.get_all()
moderator_service.get_all()
custom_command_service.get_all()
print("done!")


def run_scraper_routine():
    site_url = "https://gatry.com/"
    offers = []
    keywords = ["microfone"]

    while True:
        page = requests.get(site_url)
        parsed_page = BeautifulSoup(page.content, "html.parser")

        promos = parsed_page.find_all(class_="promocao")
        for promo in promos:

            info = promo.find(class_="informacoes")

            name_tag = info.find("h3", itemprop="name").find("a")
            product_name = name_tag.text.lower()

            if not next((kw for kw in keywords if kw in product_name), None):
                continue

            product_id = promo.get("id").replace("promocao-", "")

            if next(
                (offer for offer in offers if product_id == offer["product_id"]), None
            ):
                continue

            product_image_url = name_tag["href"]
            product_price = info.find("span", itemprop="price").text
            shop_url = info.find(class_="link_loja")["href"]

            offers.append(
                {
                    "product_id": product_id,
                    "product_name": product_name,
                    "product_image_url": product_image_url,
                    "product_price": product_price,
                    "shop_url": shop_url,
                }
            )

        # print(json.dumps(offers, indent=4, sort_keys=True, ensure_ascii=False))
        # print("total: " + str(len(offers)))
        time.sleep(60)


def run_api_listener():
    updates = message_service.get_updates(0)
    offset = 0 if len(updates) == 0 else message_service.get_last_update_id(updates) + 1

    print("→ listening for updates...")

    while True:
        updates = message_service.get_updates(offset)
        try:
            message_service.delete_messages(updates, timeout_service.timeout_users)

            if updates != None and len(updates) > 0:
                for update in updates:
                    try:
                        message = update["message"]

                        if message:
                            response_service.resolve_action(message)
                    except Exception:
                        continue
        finally:
            offset = message_service.get_last_update_id(updates) + 1
    # print("→ telegrambot has ended")


def main():
    print("→ starting scraper routine thread... ", end="")
    t1 = threading.Thread(target=run_scraper_routine)
    t1.start()
    print("done!")

    print("→ starting api listener thread... ", end="")
    t2 = threading.Thread(target=run_api_listener)
    t2.start()
    print("done!")


if __name__ == "__main__":
    main()
