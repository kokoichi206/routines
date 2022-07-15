# routines
定期実行タスク

## github の活動数チェッカー
毎日23時に1日の活動を観察し Line で通知する。

- [定期実行ymlファイル](.github/workflows/action-checker.yml)
- [実行ファイル](action_checker/events.py)

### 事前準備
必要なSECRETを登録する

- CHECK_USERS
  - どのgithubアカウントに対してチェックを行うか
    - `/`区切り
- CHECK_STEPS
  - どれくらいの活動数で写真を切り替えるか
    - `/`区切り
  - 対応する画像をリモートに保存する


## Health Checker
サイトがダウンしていないかを毎日9時に調べ、異常があった場合 Line で通知する。

- [定期実行ymlファイル](.github/workflows/my_site-health-checker.yml)


## 今日コード何行書いた？
毎日23時に、今日何行書いたかを調べ、ラインに通知する。

- [定期実行ymlファイル](.github/workflows/num_codes.yml)

### 方針
Github REST API を使う。

1. リポジトリ一覧を取得
  - [API](https://docs.github.com/ja/rest/repos/repos#list-repositories-for-the-authenticated-user)
2. 各リポジトリに対し、週間のコード変化量を取得し、和を求める
  - [API](https://docs.github.com/ja/rest/metrics/statistics#get-the-weekly-commit-activity)
3. 前日分の結果を artifacts から取得し、その差分を本日の進捗とする
4. 明日の比較用に artifacts に保存する


## サブアカウントの草の成長状況監視
毎日23時に、サブアカウントの草がきちんと成長しているかを描画し、ラインに通知する。

- [定期実行ymlファイル](.github/workflows/sub_account-grass-watcher.yml)
- [サブアカウント](https://github.com/kokoichi2)
- [草画像生成スクリプト](./watch_sub_account/grass.sh)
