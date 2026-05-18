import requests
from bs4 import BeautifulSoup


def get_exchange_rates():
    url = "https://bank.gov.ua/ua/markets/exchangerates"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f">>> ПОМИЛКА: Не вдалося завантажити сторінку (Код: {response.status_code}) <<<")
            return

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"id": "exchangeRates"})

        if not table:
            print(">>> ПОМИЛКА: Не вдалося знайти таблицю курсів на сторінці <<<")
            return

        headers_list = ["Код цифровий", "Код літерний", "Назва валюти", "Офіційний курс"]
        data = []

        # Парсим данные аккуратно по селекторам, чтобы коды не терялись
        rows = table.find("tbody").find_all("tr")
        for row in rows:
            # На сайте НБУ коды могут лежать в data-label или th/td
            cols = row.find_all(["td", "th"])
            if len(cols) >= 5:
                # Берем чистый текст без мусора
                digital_code = cols[0].text.strip()
                letter_code = cols[1].text.strip()
                name = cols[3].text.strip()
                rate = cols[4].text.strip()

                # Если первый столбец пустой, пробуем вытащить альтернативно
                if not digital_code and row.find("td", {"data-label": "Код цифровий"}):
                    digital_code = row.find("td", {"data-label": "Код цифровий"}).text.strip()

                data.append([digital_code, letter_code, name, rate])

        # Автоматически находим максимальную длину для каждой колонки под текст
        col_widths = [len(h) for h in headers_list]
        for row in data:
            for i in range(4):
                if len(row[i]) > col_widths[i]:
                    col_widths[i] = len(row[i])

        # Формируем шаблон строки на основе вычисленной ширины
        row_format = f"| {{:<{col_widths[0]}}} | {{:<{col_widths[1]}}} | {{:<{col_widths[2]}}} | {{:<{col_widths[3]}}} |"

        # Рисуем красивую и ровную таблицу
        border = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"

        print(border)
        print(row_format.format(*headers_list))
        print(border)
        for row in data:
            print(row_format.format(*row))
        print(border)

    except Exception as e:
        print(f">>> ВИД КРИТИЧНОЇ ПОМИЛКИ: {e} <<<")


if __name__ == "__main__":
    get_exchange_rates()