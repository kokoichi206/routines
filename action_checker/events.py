import datetime
import json
import logging
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import Tuple
from urllib.error import HTTPError, URLError
import base64

from dateutil import tz
from discord import DiscordNotifyBot


class ActionChecker:
    """Class for checking GitHub actions."""

    DATE_FORMAT = "%Y-%m-%d"
    GRAPHQL_URL = "https://api.github.com/graphql"

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

    def fetch_contributions(self, token: str) -> None:
        """Fetch contribution data using GitHub GraphQL API.

        GitHub はログインしていないユーザーに対して tz cookie を無視し、
        常に UTC で contribution データを返す。
        GraphQL API を使えば認証付きでタイムゾーン指定した正確なデータが取得できる。
        """
        now_jst = datetime.now().astimezone(tz.gettz('Asia/Tokyo'))

        # 直近2年分を取得（streak 計算に十分な量）
        query_parts = []
        for i in range(2):
            year = now_jst.year - i
            from_date = f"{year}-01-01T00:00:00+09:00"
            if i == 0:
                to_date = now_jst.strftime("%Y-%m-%dT23:59:59+09:00")
            else:
                to_date = f"{year}-12-31T23:59:59+09:00"
            query_parts.append(
                f'y{year}: contributionsCollection(from: "{from_date}", to: "{to_date}") {{'
                f'  contributionCalendar {{ weeks {{ contributionDays {{ date contributionCount }} }} }}'
                f'}}'
            )

        query = f'{{ user(login: "{self.user}") {{ {" ".join(query_parts)} }} }}'

        req = urllib.request.Request(
            ActionChecker.GRAPHQL_URL,
            data=json.dumps({'query': query}).encode(),
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'User-Agent': 'Action Checker',
            },
        )
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())

        user_data = result['data']['user']
        for key in user_data:
            calendar = user_data[key]['contributionCalendar']
            for week in calendar['weeks']:
                for day in week['contributionDays']:
                    d = datetime.strptime(day['date'], ActionChecker.DATE_FORMAT).date()
                    if d > self.date_today:
                        continue
                    self.counts[d] = day['contributionCount']

        print(f"fetched {len(self.counts)} days of contribution data via GraphQL API")

    def today_count(self) -> Tuple[int, int, int]:
        """Get today's contributions, continued days, and previous streak.

        The values are calculated using self.counts

        Returns:
            (today_counts, continuous_days, prev_streak)
            prev_streak: today == 0 の場合、直前の contribution streak の長さ
        """
        today = self.counts[self.date_today]
        d = self.date_today
        continued = 1
        prev_streak = 0
        if today == 0:
            while True:
                d = d - timedelta(days=1)
                cnt = self.counts.get(d, None)
                if cnt is None:
                    logging.info("予期しない事象が発生しました。", "counts: ", self.counts, "d: ", d)
                    return today, continued, prev_streak

                if cnt == 0:
                    continued += 1
                else:
                    # 直前の contribution streak を数える
                    while cnt is not None and cnt > 0:
                        prev_streak += 1
                        d = d - timedelta(days=1)
                        cnt = self.counts.get(d, None)
                    return today, continued, prev_streak
        else:
            while True:
                d = d - timedelta(days=1)
                cnt = self.counts.get(d, None)
                if cnt is None:
                    logging.info("予期しない事象が発生しました。", "counts: ", self.counts, "d: ", d)
                    return today, continued, prev_streak

                if cnt > 0:
                    continued += 1
                else:
                    return today, continued, prev_streak

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

    def daily_message(self, counts, continue_days, prev_streak=0) -> str:
        if counts == 0:
            if continue_days == 1 and prev_streak > 0:
                return f"{self.user}の本日の活動数は{counts}です。\nこのまま今日を終えると{prev_streak}日続いた連続 contributions がリセットされます！"
            else:
                return f"{self.user}の本日の活動数は{counts}です。\nこのまま今日を終えると{continue_days}日連続で No contributions になります\n本当によろしいですか？"
        else:
            return f"{self.user}の本日の活動数は{counts}です。\n{continue_days}日連続 contributions 偉い！"

    def weekly_message(self, counts: int) -> str:
        return f"{self.user}の先週の活動数は{counts}でした。今週も頑張りましょう！"


def init_images(base_url, steps, username, basic_auth_user=None, basic_auth_pass=None):
    """
    Github に写真を保存したくないため、都度ダウンロードする。
    """

    os.makedirs(username, exist_ok=True)
    print("===== init_images =====")
    img_saved_errs = {}
    headers = {
        'User-Agent': 'Action Checker (run in github actions)',
    }

    # Basic認証情報をヘッダーに設定
    if basic_auth_user and basic_auth_pass:
        encoded = base64.b64encode(f"{basic_auth_user}:{basic_auth_pass}".encode("utf-8")).decode("utf-8")
        headers['Authorization'] = f"Basic {encoded}"

    for step in steps:
        req = urllib.request.Request(
            url=f"{base_url}/{username}/{step}.png",
            headers=headers,
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
                req = urllib.request.Request(
                    url=f"{base_url}/{username}/{step}.png",
                    headers=headers,
                )
                data = urllib.request.urlopen(req).read()
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
    # 1. Discord Webhook URL
    # 2. 監視対象のgithub名(ARG_SEPARATOR 区切り)
    #      - 渡す際の区切り文字に注意
    # 3. 画像の切り替えを行う活動数(ARG_SEPARATOR 区切り)
    #      - 渡す際の区切り文字に注意
    # 4. 画像が保存されてる URL
    # 5. Basic 認証のユーザー名
    # 6. Basic 認証のパスワード
    if len(sys.argv) < 4:
        sys.exit()

    DISCORD_WEBHOOK_URL = sys.argv[1]
    users = sys.argv[2].split(ARG_SEPARATOR)
    steps = list(map(int, sys.argv[3].split(ARG_SEPARATOR)))
    base_url = sys.argv[4]
    basic_auth_user = None
    basic_auth_pass = None
    print(len(sys.argv))
    if len(sys.argv) >= 7:
        basic_auth_user = sys.argv[5]
        basic_auth_pass = sys.argv[6]

    github_token = os.environ.get('GITHUB_TOKEN', '')

    img_saved_errs = {}
    # 人ごとに写真を変更する。
    for user in users:
        img_saved_errs[user] = init_images(
            base_url, steps, user,
            basic_auth_user=basic_auth_user,
            basic_auth_pass=basic_auth_pass)

    # のちのループのために上限値を作る
    steps.append(99999)

    bot = DiscordNotifyBot(webhook_url=DISCORD_WEBHOOK_URL)
    for user in users:
        print(f"===== {user} =====")
        checker = ActionChecker(user=user)
        checker.fetch_contributions(github_token)

        today, continued, prev_streak = checker.today_count()
        print(today, continued, prev_streak)

        message = checker.daily_message(today, continued, prev_streak)
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
