import logging
import sys
from datetime import datetime

from events import ActionChecker, LINENotifyBot


def should_send_extra_message(date_today: datetime.date):
    # 0 means Monday
    return date_today.weekday() == 0


if __name__ == "__main__":

    ARG_SEPARATOR = "/"
    # 引数に必要な情報を渡す
    # 1. LINE notify の token
    # 2. 監視対象のgithub名(ARG_SEPARATOR 区切り)
    #      - 渡す際の区切り文字に注意
    if len(sys.argv) < 2:
        sys.exit()

    LINE_NOTIFY_TOKEN = sys.argv[1]
    users = sys.argv[2].split(ARG_SEPARATOR)

    if not should_send_extra_message(ActionChecker.get_today()):
        logging.info("本日は処理不要のためスキップします。")
        sys.exit()

    bot = LINENotifyBot(access_token=LINE_NOTIFY_TOKEN)

    for user in users:
        checker = ActionChecker(user=user)
        checker.fetch_counts()
        total = checker.sum_weekly_counts()
        print(f"total: {total}")

        message = checker.weekly_message(total)
        print(f"message: {message}")
        bot.send(message=message)
