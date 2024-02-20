"""Notify using LINE API

see documentation:
https://notify-bot.line.me/doc/ja/
"""

import urllib.parse

import requests


class LINENotifyBot:
    """Class for executing LINE API."""

    API_BASE_URL = 'https://notify-api.line.me'

    def __init__(self, access_token):
        """Initialize instance variables.

        Args:
            access_token (str): access token of LINE notify.
        """
        self.__headers = {'Authorization': 'Bearer ' + access_token}

    def send(
        self, message: str,
        image=None, sticker_package_id=None, sticker_id=None,
    ):
        """Send message
        """
        url = urllib.parse.urljoin(LINENotifyBot.API_BASE_URL, "api/notify")
        payload = {
            'message': message,
            'stickerPackageId': sticker_package_id,
            'stickerId': sticker_id,
        }
        files = {}
        if image != None:
            files = {'imageFile': open(image, 'rb')}
        r = requests.post(
            url,
            headers=self.__headers,
            data=payload,
            files=files,
        )
        print(f'api_url: {url}')
        print(f'status_code: {r.status_code}')
        print(f'response: {r.text}')
