import csv
import re
import requests
from bs4 import BeautifulSoup

URL = 'https://cars.av.by/filter?brands[0][brand]=8&year[min]=2020'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
           'accept': '*/*'}
HOST = 'https://cars.av.by'
FILE = 'cars.csv'


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_options(link):
    html = get_html(link)
    options = {'Экстерьер': '', 'Системы безопасности': '', 'Подушки': '', 'Системы помощи': '', 'Интерьер': '',
               'Комфорт': '', 'Обогрев': '', 'Климат': '', 'Мультимедиа': ''}

    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        sections = soup.find_all('div', class_='card__options-section')

        for section in sections:
            category = section.find('h4', class_='card__options-category').get_text()
            options_list = section.find_all('li', class_='card__options-item')
            category_options = ','.join(f'{option_item.get_text()}' for option_item in options_list)

            options[category] = category_options

    return options


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='listing-item')

    cars = []
    for item in items:
        price = re.sub(r'\D', '', item.find('div', class_='listing-item__price').get_text())
        price_usd = re.sub(r'\D', '', item.find('div', class_='listing-item__priceusd').get_text())
        link = HOST + item.find('a', class_='listing-item__link').get('href')
        year = re.sub(r'\D', '', item.find('div', class_='listing-item__params').next_element.get_text())
        options = get_options(link)

        cars.append({
            'title': item.find('h3', class_='listing-item__title').get_text(),
            'link': link,
            'price': int(price),
            'price_usd': int(price_usd),
            'city': item.find('div', class_='listing-item__location').get_text(),
            'year': int(year),
            'options': options
        })
    return cars


def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Марка', 'Ссылка', 'Цена (BYN)', 'Цена (USD)', 'Город', 'Год', 'Экстерьер',
                         'Системы безопасности', 'Подушки', 'Системы помощи', 'Интерьер', 'Комфорт',
                         'Обогрев', 'Климат', 'Мультимедиа'])
        for item in items:
            row = []
            for value in item.values():
                if type(value) != dict:
                    row.append(value)
                else:
                    for option in value.values():
                        row.append(option)
            writer.writerow(row)


def parse():
    html = get_html(URL)
    cars = []
    page = 1
    while html.status_code == 200:
        cars.extend(get_content(html.text))
        page += 1
        html = get_html(URL, params={'page': page})
    else:
        save_file(cars, FILE)


if __name__ == '__main__':
    parse()
