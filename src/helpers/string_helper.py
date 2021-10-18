from random import randint


def random_number_validation(text: str):
    if "$random_number" in text:
        try:
            str_numbers = text.split("$random_number[")[1].split("]", 1)[0]
            first_number, second_number = str_numbers.split(",")

            first_number = int(first_number)
            second_number = int(second_number)

            if (
                first_number >= second_number
                or first_number < 0
                or first_number > 1000
                or second_number < 0
                or second_number > 1000
            ):
                return False

            random_number = randint(first_number, second_number)

            return random_number >= first_number and random_number <= second_number
        except:
            return False
    else:
        return True


def random_word_validation(text: str):
    if "$random_word" in text:
        try:
            str_words = text.split("$random_word[")[1].split("]", 1)[0]
            words = str_words.split(",")

            total_words = len(words)

            if total_words < 2 or total_words > 10:
                return False

            selected_word = words[randint(0, total_words - 1)]

            return selected_word in text
        except:
            return False
    else:
        return True


def format_currency(str_currency) -> str:
    fixed_currency = "R${:,.2f}".format(str_currency)
    main_currency, fractional_currency = (
        fixed_currency.split(".")[0],
        fixed_currency.split(".")[1],
    )
    new_main_currency = main_currency.replace(",", ".")
    return new_main_currency + "," + fractional_currency


def html_sanitize(str_html: str) -> str:
    html_sanitized = str_html.replace("<br>", "\n")

    html_sanitized = html_sanitized.replace("<br >", "\n")
    html_sanitized = html_sanitized.replace("<br/>", "\n")
    html_sanitized = html_sanitized.replace("<br />", "\n")
    html_sanitized = html_sanitized.replace("&nbsp;", " ")
    html_sanitized = html_sanitized.replace("\n\n\n", "\n\n")
    html_sanitized = html_sanitized.replace("\n\n\n\n", "\n\n")
    html_sanitized = html_sanitized.replace("\n\n\n\n\n", "\n\n")

    return html_sanitized
