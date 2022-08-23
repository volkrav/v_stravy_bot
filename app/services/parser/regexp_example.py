# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re

regex = r"'(uid)': '([a-zA-Z0-9]+)'"

test_str = ("'portion': '0',\n"
	" 'price': '350.0000',\n"
	" 'priceold': '',\n"
	" 'quantity': '',\n"
	" 'single': '',\n"
	" 'sku': '',\n"
	" 'sort': '1020300',\n"
	" 'text': 'Замовлення від 1 кг.',\n"
	" 'title': 'Домашній Наполеон 1кг.',\n"
	" 'uid': '716397130761',\n"
	" 'unit': '',\n"
	" 'url': 'https://vasylevsky-stravy.com.ua/tproduct/325998011-716397130761-domashni-napoleon-1kg'}")

matches = re.finditer(regex, test_str, re.MULTILINE)

for match in matches:
    print(match.group(2))

# for matchNum, match in enumerate(matches, start=1):

#     print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))

#     for groupNum in range(0, len(match.groups())):
#         groupNum = groupNum + 1

#         print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

"""
out:
    Match 1 was found at 189-210: 'uid': '716397130761'
    Group 1 found at 190-193: uid
    Group 2 found at 197-209: 716397130761
"""

# Note: for Python 2.7 compatibility, use ur"" to prefix the regex and u"" to prefix the test string and substitution.
