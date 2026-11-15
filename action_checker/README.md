# action_checker

GitHub の活動量を監視し、日次チェックを Discord に通知する。

## セットアップ

[uv](https://docs.astral.sh/uv/getting-started/installation/) をインストールする。

```sh
cd action_checker
uv sync --locked --python 3.11
```

依存関係は `pyproject.toml` と `uv.lock` で管理する。
追加には `uv add`、更新には `uv lock --upgrade` を使い、両方のファイルをコミットする。

## 日次チェック

`GITHUB_TOKEN` にユーザーの PAT を設定し、引数で通知先・監視対象・画像設定を渡す。
複数ユーザーと画像の切り替えに使う活動数は `/` で区切る。

```sh
uv run --locked python events.py \
  "$DISCORD_WEBHOOK_URL" \
  "$CHECK_USERS" \
  "$CHECK_STEPS" \
  "$CHECK_IMG_BASE_URL" \
  "$CHECK_IMG_URL_BASIC_AUTH_USER" \
  "$CHECK_IMG_URL_BASIC_AUTH_PASS"
```

## GitHub Actions

`action-checker.yml` と `action-checker_weekly.yml` は `uv sync --locked` で依存関係を同期し、`uv run --locked` 経由でスクリプトを実行する。
Python は既存の指定を維持し、日次は 3.11、週次は 3.8 を使用する。

週次の `weekly.py` は LINE 通知を使用するコードだが、`events.py` に存在しない `LINENotifyBot` と `fetch_counts()` を参照しているため、そのままでは実行できない。
