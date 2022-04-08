import requests
import time
import random
import datetime
import xlsxwriter
from bs4 import BeautifulSoup
from fake_headers import Headers


def get_data(url: str):
    print("Начинаю сбор данных...")

    # Creating fake header for get requests
    header = Headers(browser="chrome", os="win", headers=True)

    page = 0
    cnt = 0

    # Forming file name
    file_name = f'{datetime.date.today()}_{url.split("/")[-1]}'

    flowers_data = []
    # cycling through all pages
    while True:
        this_page_url = url + f"/pg{page}"
        page += 1

        time.sleep(random.randint(0, 1))
        req = requests.get(this_page_url, header.generate())

        # 404 for (last page + 1)
        if req.status_code not in [200, 404]:
            print(f"Не удалось подключиться к странице: {this_page_url}")
            continue

        # collecting flowers cards
        soup = BeautifulSoup(req.text, "lxml")
        flower_cards = soup.find_all("div", class_="div_blk")

        # if page is empty
        if len(flower_cards) == 0:
            break

        # collecting urls for current page flowers
        flower_urls = ["https://floramoscow.ru" + card.find("a", "itm_t").get("href") for card in flower_cards]

        print(f"Собираю данные со страницы № {page}")

        # cycling through all links on the page
        for link in flower_urls:
            time.sleep(random.randint(0, 1))

            # if couldn't connect
            req = requests.get(link, header.generate())
            if req.status_code != 200:
                print(f"Не удалось подключиться к странице с товаром: {link}")
                continue

            soup = BeautifulSoup(req.text, "lxml")

            # collecting data
            this_url = link
            title = soup.find("title").text.strip()
            name = soup.find("h1", class_="itm_h1").text.strip()
            description = soup.find_all("meta")[4].get("content")
            keywords = soup.find_all("meta")[3].get("content")
            art = soup.find("span", class_="artik").text.strip().split()[-1]

            # if the is no size
            try:
                size = f'\'{soup.find("div", class_="razmer").find("div", class_="r1").text.strip()}:' \
                       f'{soup.find("div", class_="razmer").find("div", class_="r2").text.strip()}'
            except Exception:
                size = "Н/Д"

            compound = soup.find("div", class_="dop_win_sost").get("onclick").strip().replace(
                'show_hint_sost("butt_sost", "', '').replace('"); return false', "")

            full_description = soup.find("div", class_="dop_win_opis").get("onclick").strip().replace(
                'show_hint_sost("butt_opis", "', '').replace('<br><br>', ' ').replace('<br>', ' ').replace(
                '"); return false', '').replace('<p>', ' ')

            price = soup.find("div", class_="pric1").text.strip().split()[0]

            # forming new data to a dict
            new_data = {
                "URL": this_url,
                "Title": title,
                "Name": name,
                "Description": description,
                "Keywords": keywords,
                "Актикул": art,
                "Ширина:Высота": size,
                "Состав": compound,
                "Описание": full_description,
                "Цена": price
            }
            flowers_data.append(new_data)
            cnt += 1

    print("Сохраняю данные в файл...")

    headers = {
        "URL": "URL",
        "Title": "Title",
        "Name": "Name",
        "Description": "Description",
        "Keywords": "Keywords",
        "Актикул": "Актикул",
        "Ширина:Высота": "Ширина:Высота",
        "Состав": "Состав",
        "Описание": "Описание",
        "Цена": "Цена"
    }
    create_xlsx_file(file_name + ".xlsx", headers, flowers_data)

    print(f"Данные собраны. Сформирован файл: {file_name}.xlsx\n"
          f"Записано {cnt} товаров")


# Create xlsx file from list of dict
def create_xlsx_file(file_path: str, headers: dict, items: list):
    with xlsxwriter.Workbook(file_path) as workbook:
        worksheet = workbook.add_worksheet()
        worksheet.write_row(row=0, col=0, data=headers.values())
        header_keys = list(headers.keys())
        for index, item in enumerate(items):
            row = map(lambda field_id: item.get(field_id, ''), header_keys)
            worksheet.write_row(row=index + 1, col=0, data=row)


def main():
    print("Сборщик данных с сайта floramoscow.ru")
    while True:
        print("-------------------------------------\n"
              "Введите URL (для выхода введите 0): ", end="")
        line = input()

        if line == "0":
            break
        elif line.startswith("https://floramoscow.ru"):
            get_data(line)
        else:
            print("Повторите ввод. Ссылка должна начинаться с https://floramoscow.ru")


if __name__ == "__main__":
    main()
