import requests
from bs4 import BeautifulSoup
import sys
import os
import time
from PIL import Image

target_path = 'F:/card_back'
RETRY_TIMES = 5
BASEURL = "http://www.steamcardexchange.net/index.php?showcase"
categoryURLList = ["-filter-ac", "-filter-df", "-filter-gi", "-filter-jl", "-filter-mo", "-filter-pr", "-filter-su",
                   "-filter-vx", "-filter-yz", "-filter-09"]
hd = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'accept-encoding': 'gzip, deflate, br',
      'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
      'cache-control': 'max-age=0',
      'cookie': '_ga=GA1.2.130571688.1582203886; PHPSESSID=pt24be3ve4sa66snhbcngjv2rpbfm35p; _gid=GA1.2.229893832.1587004157',
      'sec-fetch-dest': 'document',
      'sec-fetch-mode': 'navigate',
      'sec-fetch-site': 'none',
      'sec-fetch-user': '?1',
      'upgrade-insecure-requests': '1',
      'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Mobile Safari/537.36'}

def adjustFileNameToWinOS(filename):
    deletechars = '\\/:*?"<>|\t.'
    for c in deletechars:
        filename = filename.replace(c, u'')
    return filename

def mkdir(gamename):
    gamename = adjustFileNameToWinOS(gamename)
    if os.path.exists(os.path.join(target_path, gamename)):
        pass
    else:
        os.mkdir(os.path.join(target_path, gamename))

def downloadImage(gameName, imageName, url, fType):
    print('Downloading: ' + gameName)
    mkdir(gameName)
    gameName = adjustFileNameToWinOS(gameName)
    dirname = os.path.join(target_path, gameName)
    if fType == "card":
        imageName = imageName[:imageName.find("- Series")-1]
        file_name = u"[Cards] - {0}".format(imageName.lstrip())
    else:  # fType == bg
        imageName = imageName[:imageName.find("- Type:")-1]
        file_name = u"[Backgrounds] - {0}".format(imageName.lstrip())
    file_name = adjustFileNameToWinOS(file_name)

    if os.path.exists(os.path.join(dirname, file_name) + '.jpg'):
        pass
    else:
        for i in range(RETRY_TIMES):
            try:
                r = requests.get(url, proxies={'http':'127.0.0.1:1080', 'https':'127.0.0.1:1080'}, headers=hd)
                break
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
                print(u"Address from %s was not available when tried to download. Error: %s", gameName, e)

        if r.status_code == 200:
            f = open(os.path.join(dirname, file_name) + '.jpg', "wb")
            f.write(r.content)
            f.close()
        else:
            print(u"Address from %s was not available when tried to download. Error: %s", gameName, 'not 200')

        '''
        imgFileType = Image.open(os.path.join(dirname, imageName)).format.lower()
        i = 0
        file_name_new = file_name
        while os.path.isfile(file_name_new + u".{0}".format(imgFileType)):
            i += 1
            file_name_new = file_name + u" [{0}]".format(i)
        file_name_new = file_name_new + u".{0}".format(imgFileType)
        os.rename(file_name, file_name_new)
        '''

def main():
    gamesDict = {}
    testList = categoryURLList[7:8]
    for filterURL in testList:
        print(u"Grabbing {}".format(BASEURL + filterURL))
        try:
            r = requests.get(BASEURL + filterURL, proxies={'http':'127.0.0.1:1080', 'https':'127.0.0.1:1080'}, headers=hd)
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            print(u'Grabbing %s failed. Error: %s', filterURL, e)
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        games = soup.findAll("div", attrs={"class": "showcase-game-item"})
        for game in games:
            gameLink = game.select("a")[0]
            name = gameLink.find("img").get("alt")
            gamesDict[name] = gameLink.get("href")

    temp = sorted(gamesDict.keys())
    start_index = 0  # temp.index('God Mode')
    finish_index = len(temp)  # temp.index('TurnOn')
    cropped_list = temp[start_index:finish_index]
    for key in cropped_list:
        for i in range(RETRY_TIMES):
            try:
                page = requests.get("http://www.steamcardexchange.net/" + gamesDict[key], proxies={'http':'127.0.0.1:1080', 'https':'127.0.0.1:1080'}, headers=hd)
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
                print(u'Game "%s" page is not available. Error: %s', key, e)
                time.sleep(1)

        soup = BeautifulSoup(page.text, "html.parser")
        cards = soup.findAll("a", {"rel": "lightbox-normal"})
        hdBgrounds = soup.findAll("a", {"rel": "lightbox-background"})

        alreadyDoneCardLinks = []
        alreadyDoneBgLinks = []

        for card in cards:
            try:
                hdImageLink = card.get("href")
                hdImageName = card.get("title")
                if not hdImageLink in alreadyDoneCardLinks:
                    for i in range(RETRY_TIMES):
                        try:
                            downloadImage(key, hdImageName, hdImageLink, "card")
                            break
                        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
                            print(u'Address of "%s" is not available. Error: %s', hdImageName, e)
                            time.sleep(1)
                    alreadyDoneCardLinks.append(hdImageLink)
            except Exception as e:
                print(u"Card ERROR: {0}".format(str(e)))
                print(u'Another weird error occurred for "%s". Error: %s', key, e)
                if str(e) == u"[Errno 28] No space left on device":
                    sys.exit(1)

        for hdBg in hdBgrounds:
            try:
                hdBgLink = hdBg.get("href")
                hdBgName = hdBg.get("title")
                if not hdBgLink in alreadyDoneBgLinks:
                    for i in range(RETRY_TIMES):
                        try:
                            downloadImage(key, hdBgName, hdBgLink, "bg")
                            break
                        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
                            print(u'Address of "%s" is not available. Error: %s', hdBgName, e)
                            time.sleep(1)
                    alreadyDoneBgLinks.append(hdBgLink)
            except Exception as e:
                print(u"Background ERROR: {0}".format(str(e)))
                print(u'Another weird error occurred for "%s". Error: %s', key, e)
                if str(e) == u"[Errno 28] No space left on device":
                    sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping...")
        time.sleep(5)
        sys.exit(0)

