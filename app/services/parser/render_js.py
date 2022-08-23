""" from requests_html import HTMLSession

session = HTMLSession()

resp = session.get('https://vasylevsky-stravy.com.ua/novinki')
# print(resp.text)
# print(resp.html.absolute_links)
# print((resp.html.find('.t-records', first=True)).attrs)
# Домашній Наполеон 1кг.
resp.html.render()
# for x in resp.html.xpath('//*[@id="rec474752743"]/script'):
# storepart: '275228065091',
print(resp.html.find('.storepart'))
 """
