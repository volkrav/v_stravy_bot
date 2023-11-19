import logging

import requests
import lxml
from app.services.parser.DBcm_sync import UseDataBase
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

categories_id = {
    'novinki': 275228065091, 'pershispravy': 588357731541, 'vypichka': 495017585511,
    'pelmeni': 578674463761, 'vareniki': 130544233911, 'kotlety': 417222398871,
    'chebureki': 401835988651, 'kruchenyky': 596431547931, 'mlynchi': 389282944221,
    'zrazy': 454205351901, 'syrnyky': 183110287401, 'solinnya': 840563061581, 'inshistravy': 426777982861
}

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}


def main():
    try:
        base_url = 'https://vasylevsky-stravy.com.ua/'

        try:
            response = requests.get(base_url, headers=header)
        except Exception as err:
            logger.error(
                f'products.main.requests.get BAD get {err.args}')

        soup = BeautifulSoup(response.text, 'lxml')
        try:
            data = soup.find(
                'ul', class_='t967__list t-menu__list t967__menualign_left').find_all(
                'li', class_='t967__list-item')
        except Exception as err:
            logger.error(f'data = soup.find get {err.args}')
        # Отримую список словників з категоріями
        for row in data:
            category_name = row.find('a', class_='t-menu__link-item').text.strip()
            category_alias = row.find(
                'a', class_='t-menu__link-item').get('href').strip('/ ')
            category_code = [code for val,
                            code in categories_id.items() if val == category_alias][0]
            print(category_alias)
            try:
                with UseDataBase() as cursor:
                    cursor.execute(
                        f'INSERT INTO categories '
                        f'(partuid, name, alias) '
                        f'VALUES (?, ?, ?) '
                        f'ON CONFLICT (partuid) DO UPDATE SET '
                        f'partuid=excluded.partuid, name=excluded.name, alias=excluded.alias',
                        (category_code, category_name, category_alias)
                    )
            except Exception as err:
                logger.error(
                    f'categories.main BAD get {err.args}')
    except Exception as err:
        logger.error(
            f'main '
            f'BAD _ get {err.args}')


if __name__ == '__main__':
    main()
