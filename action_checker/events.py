import urllib.request, urllib.parse
import json
import datetime
import requests
import sys
from bs4 import BeautifulSoup


class LINENotifyBot:
    API_URL = 'https://notify-api.line.me/api/notify'
    def __init__(self, access_token):
        self.__headers = {'Authorization': 'Bearer ' + access_token}

    def send(
            self, message,
            image=None, sticker_package_id=None, sticker_id=None,
            ):
        payload = {
            'message': message,
            'stickerPackageId': sticker_package_id,
            'stickerId': sticker_id,
            }
        files = {}
        if image != None:
            files = {'imageFile': open(image, 'rb')}
        r = requests.post(
            LINENotifyBot.API_URL,
            headers=self.__headers,
            data=payload,
            files=files,
        )

""" Github api を使用する方法
dt_now = datetime.datetime.now()

# datetime format: 2022-03-03T11:56:15Z
def is_todays_event(datetime: str):
    return dt_now.year == int(datetime[0:4]) and \
            dt_now.month == int(datetime[5:7]) and \
            dt_now.month == int(datetime[8:10])

def action_counts_today(username: str):
    headers = {
        "Authorization" :"token XXXXYYYYY",
        "Accept" :"application/vnd.github.v3+json"
    }
    req = urllib.request.Request(f"https://api.github.com/users/{username}/events", headers=headers)
    counts = 0
    with urllib.request.urlopen(req) as res:
        html = res.read().decode("utf-8")
        events = json.loads(html)
        for event in events:
            if is_todays_event(event['created_at']):
                counts += 1
    return counts
"""

now = datetime.datetime.now()
formatted_date = now.strftime("%Y-%m-%d")

# 本日の活動量を、html の草から直接取得
def counts_today(username: str):

    TOP_URL = f'https://github.com/{username}'

    headers = {'User-Agent': 'Mozilla/5.0'}

    soup = BeautifulSoup(
        requests.get(TOP_URL, headers=headers).content, 'html.parser')

    details = soup.findAll('rect', class_='ContributionCalendar-day')

    for detail in details:
        if detail.has_attr('data-count'):
            if detail.attrs['data-date'] == formatted_date:
                return detail.attrs['data-count']
    return -1

# Github に写真を保存したくないため、都度ダウンロードする
def init_images():
    good_img_path = "https://kokoichi0206.mydns.jp/imgs/line/god.png"
    bad_img_path = "https://kokoichi0206.mydns.jp/imgs/line/president.png"
    imgs = [
        {
            "path": good_img_path,
            "name": "god"
        },
        {
            "path": bad_img_path,
            "name": "president"
        },
    ]
    for img in imgs:
        urllib.request.urlretrieve(
            img["path"], f"{img['name']}.png")


if __name__ == "__main__":
    # 引数に LINE notify の token を渡す
    if len(sys.argv) == 1:
        sys.exit()

    LINE_NOTIFY_TOKEN = sys.argv[1]
    init_images()
    users = ["kokoichi206", "kqns91", "p238049y"]

    bot = LINENotifyBot(access_token=LINE_NOTIFY_TOKEN)
    for user in users:
        counts = counts_today(user)

        if counts == "0" or counts == 0:
            bot.send(
                message = f'{user}の本日の活動数は{counts}です。\nこのまま本日を終えても良いですか？',
                image = 'president.png',
            )
        else:
            bot.send(
                message = f'{user}の本日の活動数は{counts}です。',
                image = 'god.png',
            )
