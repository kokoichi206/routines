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

import requests
from bs4 import BeautifulSoup
from dateutil import tz
from line import LINENotifyBot


class ActionChecker:
    """Class for checking GitHub actions."""

    DATE_FORMAT = "%Y-%m-%d"
    # 『1 contribution on January 8, 2023』の形
    contribution_regex = re.compile(r'\d*')

    def __init__(self, user: str) -> None:
        """Initialize instance variables.

        Args:
            user (str): GitHub username.
        """
        self.user = user

        self.date_today = ActionChecker.get_today()
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

    def fetch_counts(self) -> None:
        """Get contributions directly from html object.
        
        Save them as a instance variable: self.counts
        """

        TOP_URL = f'https://github.com/{self.user}'
        headers = {
            'User-Agent': 'Mozilla/5.0',
            "Accept-Language": "en"
        }

        soup = BeautifulSoup(
            requests.get(TOP_URL, headers=headers).content, 'html.parser')

        details = soup.findAll('rect', class_='ContributionCalendar-day')

        self.counts = {}
        # 過去の草一覧
        for detail in details:
            if 'data-date' not in detail.attrs:
                continue

            d = datetime.strptime(detail.attrs['data-date'], ActionChecker.DATE_FORMAT).date()
            # 2023-01-20
            if d > self.date_today:
                continue

            m = ActionChecker.contribution_regex.match(detail.text)
            if m.group():
                contributions = int(m.group())
                self.counts[d] = contributions
            else:
                # No contributionos on January 8, 2023 のように表示される。
                self.counts[d] = 0

    def today_count(self) -> Tuple[int, int]:
        """Get today's contributions and continued days.

        The values are calculated using self.counts

        Returns:
            (today_counts, continuous_days)
        """
        #  で返却
        today = self.counts[self.date_today]
        d =self. date_today
        continued = 0
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


def init_images(steps, username):
    """
    Github に写真を保存したくないため、都度ダウンロードする。
    """
    BASE_URL = 'https://kokoichi0206.mydns.jp/imgs/github-events'

    os.makedirs(username, exist_ok=True)
    print("===== init_images =====")
    img_saved_errs = {}
    for step in steps:
        try:
            data = urllib.request.urlopen(
                f"{BASE_URL}/{username}/{step}.png").read()
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
                    f"{BASE_URL}/{username}/{step}.png").read()
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
    if len(sys.argv) < 3:
        sys.exit()

    LINE_NOTIFY_TOKEN = sys.argv[1]
    users = sys.argv[2].split(ARG_SEPARATOR)
    steps = list(map(int, sys.argv[3].split(ARG_SEPARATOR)))

    img_saved_errs = {}
    # 人ごとに写真を変更する。
    for user in users:
        img_saved_errs[user] = init_images(steps, user)

    # のちのループのために上限値を作る
    steps.append(99999)

    bot = LINENotifyBot(access_token=LINE_NOTIFY_TOKEN)
    for user in users:
        checker = ActionChecker(user=user)
        checker.fetch_counts()
        today, continued = checker.today_count()
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
            bot.send(
                message=message,
                image='NOT_FOUND.png',
            )

    # # 画像サーバー側がおかしい場合
    # if all([type(err) is URLError for err in img_saved_errs.values()]):
    #     bot.send(
    #         message="画像を取得する設定がおかしいようです..."
    #     )
