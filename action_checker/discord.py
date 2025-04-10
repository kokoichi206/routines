"""Notify using Discord Webhook API

Discord Webhookを使用して通知を送信するためのクラス
"""

import json
import urllib.parse
import requests


class DiscordNotifyBot:
    """Class for executing Discord Webhook API."""

    def __init__(self, webhook_url):
        """Initialize instance variables.

        Args:
            webhook_url (str): Discord Webhook URL.
        """
        self.webhook_url = webhook_url
        self.headers = {'Content-Type': 'application/json'}

    def send(
        self, message: str,
        image=None, username=None, avatar_url=None,
    ):
        """Send message and optionally an image to Discord.

        Args:
            message (str): Message to send.
            image (str, optional): Path to image file. Defaults to None.
            username (str, optional): Override bot username. Defaults to None.
            avatar_url (str, optional): Override bot avatar. Defaults to None.
        """
        if image:
            # 画像がある場合はmultipart/form-dataで送信
            payload = {
                "content": message,
            }

            if username:
                payload["username"] = username

            if avatar_url:
                payload["avatar_url"] = avatar_url

            # 画像ファイルをmultipart formに追加
            with open(image, 'rb') as f:
                files = {
                    'file': (image, f, 'image/png')
                }

                # リクエスト送信
                response = requests.post(
                    self.webhook_url,
                    data={"payload_json": json.dumps(payload)},
                    files=files
                )
        else:
            # 画像がない場合はJSON形式で送信
            payload = {
                "content": message,
            }

            if username:
                payload["username"] = username

            if avatar_url:
                payload["avatar_url"] = avatar_url

            # リクエスト送信
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers=self.headers
            )

        print(f'webhook_url: {self.webhook_url}')
        print(f'status_code: {response.status_code}')
        print(f'response: {response.text}')

        return response

    def send_embed(
        self, title: str, description: str, 
        color=0x00ff00, fields=None, image=None,
        username=None, avatar_url=None,
    ):
        """Send an embed message to Discord.

        Args:
            title (str): Embed title.
            description (str): Embed description.
            color (int, optional): Embed color in hex. Defaults to 0x00ff00 (green).
            fields (list, optional): List of field dicts with name and value. Defaults to None.
            image (str, optional): Path to image file. Defaults to None.
            username (str, optional): Override bot username. Defaults to None.
            avatar_url (str, optional): Override bot avatar. Defaults to None.
        """
        embed = {
            "title": title,
            "description": description,
            "color": color,
        }

        if fields:
            embed["fields"] = fields

        if image:
            # 画像がある場合
            payload = {
                "embeds": [embed]
            }

            if username:
                payload["username"] = username

            if avatar_url:
                payload["avatar_url"] = avatar_url

            # 画像ファイルをmultipart formに追加
            with open(image, 'rb') as f:
                files = {
                    'file': (image, f, 'image/png')
                }

                # 画像URLを埋め込みに追加
                embed["image"] = {"url": f"attachment://{image}"}

                # リクエスト送信
                response = requests.post(
                    self.webhook_url,
                    data={"payload_json": json.dumps(payload)},
                    files=files
                )
        else:
            # 画像がない場合
            payload = {
                "embeds": [embed]
            }

            if username:
                payload["username"] = username

            if avatar_url:
                payload["avatar_url"] = avatar_url

            # リクエスト送信
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers=self.headers
            )

        print(f'webhook_url: {self.webhook_url}')
        print(f'status_code: {response.status_code}')
        print(f'response: {response.text}')

        return response
