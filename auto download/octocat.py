# download octocats from the website

import os
import time
import requests
from bs4 import BeautifulSoup

folder_path = 'D:/Download/octocat/'
url = 'https://octodex.github.com/'
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')
items = soup.find_all('img', attrs='d-block width-fit height-auto rounded-1 lazy')
texts = soup.find_all('span')

for index, item in enumerate(items):
    if item:
        source = item.get('data-src')
        html = requests.get(url + source)
        num = texts[index].get_text()
        num = num[1:len(num)-1]
        name = folder_path + num + ' - ' + source[8:]
        if os.path.exists(name):
            pass
        else:
            with open(name, 'wb') as file:
                file.write(html.content)
                file.flush()
            file.close()
        print(name + ' - done')
        time.sleep(1.5)


