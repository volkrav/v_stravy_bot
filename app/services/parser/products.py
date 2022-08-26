import requests
import json
import time
import re
from categories import categories_id, header
from DBcm_sync import UseDataBase


def main():

    def get_products(categories_id: dict, header: str) -> dict:
        tilda_url = f'https://store.tildacdn.com/api/getproductslist/?storepartuid='
        time.sleep(1)
        for products in (requests.get(tilda_url+str(category_id), headers=header)
                         for category_id in categories_id.values()):
            yield products.json()['products']

    def get_product(products: dict) -> dict:
        for i in range(len(products)):
            yield products[i]

    for products in get_products(categories_id, header):
        for product in get_product(products):
            uid = product['uid'].strip()
            title = product['title'].strip()
            price = int(float(product['price'].strip()))

            descr = _formatted_text(product['descr']).strip()
            if 'Склад' not in descr:
                descr = 'Склад: ' + descr

            text = _formatted_text(product['text']).strip()
            if 'Склад' in text:
                regexp_result = re.match(r'.*(Спосіб приготування.*)', text)
                if regexp_result:
                    text = regexp_result.group(1)

            if 'Спосіб' in descr:
                regexp_result = re.match(r'(.+)(Спосіб приготування.*)', descr)
                if regexp_result:
                    descr = regexp_result.group(1).strip()
                    if not text:
                        text = regexp_result.group(2).strip()

            img = product['editions'][0]['img'].strip()
            quantity = product['quantity'].strip()

            gallery = ''
            for img_dict in json.loads(product['gallery']):
                for link in img_dict.values():
                    gallery += link.strip() + ','
            gallery = gallery.strip(',')

            url = product['url'].strip()
            partuids = ','.join(json.loads(product['partuids']))

            with UseDataBase() as cursor:
                cursor.execute(
                    f'INSERT INTO products '
                    f'(uid, title, price, descr, text, '
                    f'img, quantity, gallery, url, partuids) '
                    f'VALUES '
                    f'({", ".join("?" * 10)})', (
                        uid, title, price, descr, text,
                        img, quantity, gallery, url,
                        partuids
                    )
                )

def _del_html_tags(str_with_html: str) -> str:
    return re.sub(r'(\<(/?[^>]+)>)', ' ', str_with_html)

def _del_extra_space(str_with_html: str) -> str:
    str_with_html = re.sub(r'&nbsp;', '', str_with_html)
    return re.sub(r'\s{2,}', '', str_with_html)

def _formatted_text(str_with_html: str) -> str:
    str_without_html = _del_html_tags(str_with_html)
    str_without_html = re.sub(r' *\. *', '. ', str_without_html)
    str_without_html = re.sub(r'\. \. \.', '...', str_without_html)
    str_without_html = re.sub(r' *, *', ', ', str_without_html)
    str_without_html = re.sub(r' *\( *', ' (', str_without_html)
    str_without_html = re.sub(r' *\) *', ') ', str_without_html)
    str_without_html = re.sub(r'звилин', 'хвилин', str_without_html)
    str_without_html = re.sub(r'Гогох', 'Горох', str_without_html)
    str_without_html = re.sub(r'перецьболгарський', 'перець болгарський', str_without_html)
    str_without_html = re.sub(r'капустабілокачанна', 'капуста білокачанна', str_without_html)
    str_without_html = re.sub(r'консервованій', 'консервований', str_without_html)
    return _del_extra_space(str_without_html)


if __name__ == '__main__':
    main()
