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
# (今日のカウント, 0日連続日数) を返却
def counts_today(username: str):

    TOP_URL = f'https://github.com/{username}'

    headers = {'User-Agent': 'Mozilla/5.0'}

    soup = BeautifulSoup(
        requests.get(TOP_URL, headers=headers).content, 'html.parser')

    details = soup.findAll('rect', class_='ContributionCalendar-day')

    # 過去の草一覧
    counts = []
    # 本日の草
    today = 0
    for detail in details:
        if detail.has_attr('data-count'):
            counts.append(detail.attrs['data-count'])
            print(counts)
            if detail.attrs['data-date'] == formatted_date:
                today = int(detail.attrs['data-count'])
    if today == 0:
        result = 0
        for cnt in counts[::-1]:
            print(cnt)
            if cnt == "0":
                result += 1
            else:
                return today, result
    else:
        return today, 0
    return -1, -1

# Github に写真を保存したくないため、都度ダウンロードする
def init_images(steps):
    BASE_URL = "https://kokoichi0206.mydns.jp/imgs/github-events"
    for step in steps:
        urllib.request.urlretrieve(
            f'{BASE_URL}/{step}.png', f"{step}.png")


if __name__ == "__main__":

    ARG_SEPARATOR = "/"
    # 引数に必要な情報を渡す
    # 1. LINE notify の token
    # 2. 監視対象のgithub名(ARG_SEPARATOR 区切り)
    #      - 渡す際の区切り文字に注意
    # 3. 画像の切り替えを行う活動数(ARG_SEPARATOR 区切り)
    #      - 渡す際の区切り文字に注意
    if len(sys.argv) < 3:
        sys.exit()

    LINE_NOTIFY_TOKEN = sys.argv[1]
    users = sys.argv[2].split(ARG_SEPARATOR)
    steps = list(map(int, sys.argv[3].split(ARG_SEPARATOR)))
    init_images(steps)
    # のちのループのために上限値を作る
    steps.append(99999)

    bot = LINENotifyBot(access_token=LINE_NOTIFY_TOKEN)
    for user in users:
        counts, zero_days = counts_today(user)

        print(counts)
        if counts == 0:
            bot.send(
                message = f'{user}の本日の活動数は{counts}です。このまま今日を終えると{zero_days}日連続で No contributions になります\n本当によろしいですか？',
                image = '0.png',
            )
        else:
            for i in range(1, len(steps)):
                if steps[i] <= counts < steps[i+1]: 
                    bot.send(
                        message = f'{user}の本日の活動数は{counts}です。',
                        image = f'{steps[i]}.png',
                    )
