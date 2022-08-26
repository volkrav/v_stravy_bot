import requests
from bs4 import BeautifulSoup
from DBcm_sync import UseDataBase

categories_id = {
    'novinki': 275228065091, 'pershispravy': 588357731541, 'vypichka': 495017585511,
    'pelmeni': 578674463761, 'vareniki': 130544233911, 'kotlety': 417222398871,
    'chebureki': 401835988651, 'kruchenyky': 596431547931, 'mlynchi': 389282944221,
    'zrazy': 454205351901, 'syrnyky': 183110287401, 'inshistravy': 426777982861
}

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}


def main():

    base_url = 'https://vasylevsky-stravy.com.ua/'

    response = requests.get(base_url, headers=header)
    soup = BeautifulSoup(response.text, 'lxml')

    data = soup.find(
        'ul', class_='t967__list t967__menualign_left').find_all(
        'li', class_='t967__list-item')

    # Отримую список словників з категоріями
    for row in data:
        category_name = row.find('a', class_='t-menu__link-item').text.strip()
        category_alias = row.find(
            'a', class_='t-menu__link-item').get('href').strip('/ ')
        category_code = [code for val,
                         code in categories_id.items() if val == category_alias][0]
        try:
            with UseDataBase() as cursor:
                cursor.execute(
                    f"INSERT INTO categories "
                    f"(partuid, name, alias) "
                    f'VALUES (?, ?, ?) ',
                    (category_code, category_name, category_alias)
                )
        except Exception as err:
            print(err.args)


if __name__ == '__main__':
    main()
