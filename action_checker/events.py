import datetime
import logging
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import Tuple
from urllib.error import HTTPError, URLError

from selenium import webdriver
from bs4 import BeautifulSoup
from dateutil import tz
from line import LINENotifyBot
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class ActionChecker:
    """Class for checking GitHub actions."""

    DATE_FORMAT = "%Y-%m-%d"
    # 『1 contribution on January 8, 2023』の形。
    contribution_regex = re.compile(r'\d*')
    # contribution の年を指定するためのリンクの id。『year-link-2023』の形。
    year_atag_id_regex = re.compile(r'year-link-\d{4}')

    headers = {
        'User-Agent': 'Mozilla/5.0',
        "Accept-Language": "en",
        "Time-Zone": "Asia/Tokyo",
        "TZ": "Asia/Tokyo",
        "Cookie": "tz=Asia%2FTokyo",
    }

    def __init__(self, user: str) -> None:
        """Initialize instance variables.

        Args:
            user (str): GitHub username.
        """
        self.user = user
        self.DRIVER_PATH = "./chromedriver"

        self.date_today = ActionChecker.get_today() - timedelta(days=1)
        # {datetime.date(2022, 7, 25): 6, ...} の形式で活動数を保持する。
        self.counts = {}

    @classmethod
    def get_today(cls) -> datetime.date:
        """Get date of today (JST).

        Returns:
            datetime.date object
        """
        JST = tz.gettz('Asia/Tokyo')
        now = datetime.now().astimezone(JST)
        print(f"now: {now}")
        formatted_date = now.strftime(ActionChecker.DATE_FORMAT)
        # datetime.date 型として扱う
        return datetime.strptime(formatted_date, ActionChecker.DATE_FORMAT).date()

    def fetch_year_separated_urls(self) -> list:
        """Get urls to contributions of each year.

        Returns:
            list: urls to contributions of each year.
        """

        # js を動作させ DOM が揃うのを待つために selenium を使用。
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(self.DRIVER_PATH, options=options)
        wait = WebDriverWait(driver=driver, timeout=60)

        TOP_URL = f'https://github.com/{self.user}'
        driver.get(TOP_URL)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'js-year-link')))

        html = driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, 'html.parser')

        year_separated_urls = []

        atags = soup.findAll('a', class_='js-year-link')
        for atag in atags:
            id = atag.attrs['id']
            m = ActionChecker.year_atag_id_regex.match(id)
            if m.group():
                href = atag.attrs['href']
                year_separated_urls.append(f'https://github.com/{href}')

        print(f"year_separated_urls: {year_separated_urls}")
        return year_separated_urls

    def fetch_counts(self, url: str) -> None:
        """Get contributions directly from html object of the specific year's overview url.
        
        Save them as a instance variable: self.counts
        """

        # js を動作させ DOM が揃うのを待つために selenium を使用。
        # TODO: TOP_URL のページを持ったままボタン押下で遷移させる。
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(self.DRIVER_PATH, options=options)
        wait = WebDriverWait(driver=driver, timeout=60)

        driver.get(url)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'js-year-link')))

        html = driver.page_source.encode("utf-8")
        soup = BeautifulSoup(html, 'html.parser')

        tds = soup.findAll('td', class_='ContributionCalendar-day')
        tool_tips = soup.findAll('tool-tip', class_='sr-only')
        
        for_to_contributions = {}
        for tool_tip in tool_tips:
            key_for = tool_tip.attrs['for']
            m = ActionChecker.contribution_regex.match(tool_tip.text)
            if m.group():
                contributions = int(m.group())
                for_to_contributions[key_for] = contributions
            else:
                for_to_contributions[key_for] = 0

        # 過去の草一覧
        for td in tds:
            if 'data-date' not in td.attrs:
                continue

            d = datetime.strptime(td.attrs['data-date'], ActionChecker.DATE_FORMAT).date()
            # 2023-01-20
            if d > self.date_today:
                continue

            self.counts[d] = for_to_contributions[td.attrs['id']]

    def today_count(self) -> Tuple[int, int]:
        """Get today's contributions and continued days.

        The values are calculated using self.counts

        Returns:
            (today_counts, continuous_days)
        """
        #  で返却
        print(self.counts)
        today = self.counts[self.date_today]
        d = self.date_today
        continued = 1
        if today == 0:
            while True:
                d = d - timedelta(days=1)
                cnt = self.counts.get(d, None)
                if cnt is None:
                    logging.info("予期しない事象が発生しました。", "counts: ", self.counts, "d: ", d)
                    return today, continued

                if cnt == 0:
                    continued += 1
                else:
                    return today, continued
        else:
            while True:
                d = d - timedelta(days=1)
                cnt = self.counts.get(d, None)
                if cnt is None:
                    logging.info("予期しない事象が発生しました。", "counts: ", self.counts, "d: ", d)
                    return today, continued

                if cnt > 0:
                    continued += 1
                else:
                    return today, continued

    def sum_weekly_counts(self) -> int:
        """Calculate weekly contrubutions of last week.

        This method is expected to call on Mondays.

        Returns:
            (today_counts, continuous_days)
        """
        total = 0
        d = self.date_today
        # 月曜朝実行されるとし、先週分のコントリビューションを計算
        d = d - timedelta(days=1)
        for _ in range(7):
            total += self.counts[d]
            d = d - timedelta(days=1)
        return total

    def daily_message(self, counts, continue_days) -> str:
        if counts == 0:
            return f"{user}の本日の活動数は{counts}です。\nこのまま今日を終えると{continue_days}日連続で No contributions になります\n本当によろしいですか？"
        else:
            return f"{user}の本日の活動数は{counts}です。\n{continue_days}日連続 contributions 偉い！"

    def weekly_message(self, counts: int) -> str:
        return f"{self.user}の先週の活動数は{counts}でした。今週も頑張りましょう！"


def init_images(base_url, steps, username):
    """
    Github に写真を保存したくないため、都度ダウンロードする。
    """

    os.makedirs(username, exist_ok=True)
    print("===== init_images =====")
    img_saved_errs = {}
    for step in steps:
        req = urllib.request.Request(
            url=f"{base_url}/{username}/{step}.png",
            headers={
                'User-Agent': 'Action Checker (run in github actions)',
            },
        )
        try:
            data = urllib.request.urlopen(req).read()
            with open(f"{username}/{step}.png", mode="wb") as f:
                f.write(data)
            img_saved_errs[step] = None
        except HTTPError as e:
            img_saved_errs[step] = e
        except URLError as e:
            img_saved_errs[step] = e

    # 証明書の有効期限切れ等で CERTIFICATE_VERIFY_FAILED が出ることがある。
    # see: https://end0tknr.hateblo.jp/entry/20210312/1615498434
    if all([type(err) == URLError for err in img_saved_errs.values()]):

        print("===== Retry with default SSL certificate =====")
        # デフォルトの証明書を付けてリトライ
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context

        for step in steps:
            try:
                data = urllib.request.urlopen(
                    f"{base_url}/{username}/{step}.png").read()
                with open(f"{username}/{step}.png", mode="wb") as f:
                    f.write(data)
                img_saved_errs[step] = None
            except HTTPError as e:
                img_saved_errs[step] = e
            except URLError as e:
                img_saved_errs[step] = e

    print(f"steps: {steps}")
    print(f"img_saved_errs: {img_saved_errs}")
    return img_saved_errs


if __name__ == "__main__":

    ARG_SEPARATOR = "/"
    # 引数に必要な情報を渡す
    # 1. LINE notify の token
    # 2. 監視対象のgithub名(ARG_SEPARATOR 区切り)
    #      - 渡す際の区切り文字に注意
    # 3. 画像の切り替えを行う活動数(ARG_SEPARATOR 区切り)
    #      - 渡す際の区切り文字に注意
    # 4. 画像が保存されてる URL
    if len(sys.argv) < 4:
        sys.exit()

    LINE_NOTIFY_TOKEN = sys.argv[1]
    users = sys.argv[2].split(ARG_SEPARATOR)
    steps = list(map(int, sys.argv[3].split(ARG_SEPARATOR)))
    base_url = sys.argv[4]

    img_saved_errs = {}
    # 人ごとに写真を変更する。
    for user in users:
        img_saved_errs[user] = init_images(base_url, steps, user)

    # のちのループのために上限値を作る
    steps.append(99999)

    bot = LINENotifyBot(access_token=LINE_NOTIFY_TOKEN)
    for user in users:
        print(f"===== {user} =====")
        checker = ActionChecker(user=user)
        urls = checker.fetch_year_separated_urls()
        for url in urls:
            checker.fetch_counts(url)

        today, continued = checker.today_count()
        # today = 18
        print(today, continued)

        message = checker.daily_message(today, continued)
        print(message)

        step = 0
        for i in range(1, len(steps)):
            if steps[i] <= today < steps[i+1]:
                step = steps[i]

        img_err = img_saved_errs[user][step]
        if not img_err:
            print("normal image")
            bot.send(
                message=message,
                image=f"{user}/{step}.png",
            )
        elif img_err:
            print("not found image")
            # bot.send(
            #     message=message,
            #     image='NOT_FOUND.png',
            # )

    # # 画像サーバー側がおかしい場合
    # if all([type(err) is URLError for err in img_saved_errs.values()]):
    #     bot.send(
    #         message="画像を取得する設定がおかしいようです..."
    #     )
