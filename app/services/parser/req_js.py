import requests
import json
import time
from categories import categories_id, header


def main():

    def get_data(categories_id: dict, header: str):
        for code in categories_id.values():
            tilda_url = f'https://store.tildacdn.com/api/getproductslist/?storepartuid={code}]'
            time.sleep(1)
            yield requests.get(tilda_url, headers=header).json()

    def get_item(data):
        for i in range(len(data['products'])):
            yield data['products'][i]

    for data in get_data(categories_id, header):

        for item_in_cat in get_item(data):
            item_code = item_in_cat['uid'].strip()
            item_name = item_in_cat['title'].strip()
            item_price = item_in_cat['price'].strip()
            item_descr = item_in_cat['descr'].replace('<br />', ' ').strip()
            item_text = item_in_cat['text'].strip()
            item_img = item_in_cat['editions'][0]['img'].strip()
            item_quantity = item_in_cat['quantity'].strip()
            item_gallery = []
            for img_dict in json.loads(item_in_cat['gallery']):
                for link in img_dict.values():
                    item_gallery.append(link.strip())
            item_url = item_in_cat['url'].strip()
            item_categories_codes = json.loads(item_in_cat['partuids'])
            print(item_name)


if __name__ == '__main__':
    main()
