import requests
import json
import time
from categories import categories_id, header


def main():

    def get_items(categories_id: dict, header: str) -> dict:
        tilda_url = f'https://store.tildacdn.com/api/getproductslist/?storepartuid='
        time.sleep(1)
        for items in (requests.get(tilda_url+str(category_id), headers=header)
                      for category_id in categories_id.values()):
            yield items.json()['products']

    def get_item(items: dict) -> dict:
        for i in range(len(items)):
            yield items[i]

    for items in get_items(categories_id, header):
        for item in get_item(items):
            item_code = item['uid'].strip()
            item_name = item['title'].strip()
            item_price = item['price'].strip()
            item_descr = item['descr'].replace('<br />', ' ').strip()
            item_text = item['text'].strip()
            item_img = item['editions'][0]['img'].strip()
            item_quantity = item['quantity'].strip()
            item_gallery = []
            for img_dict in json.loads(item['gallery']):
                for link in img_dict.values():
                    item_gallery.append(link.strip())
            item_url = item['url'].strip()
            item_categories_codes = json.loads(item['partuids'])
            print(item_name)


if __name__ == '__main__':
    main()
