# routines
定期実行タスク

## githubの活動数チェッカー
[定期実行ymlファイル](.github/workflows/action-checker.yml)

[実行ファイル](action_checker/events.py)

### 事前準備
必要なSECRETを登録する

- CHECK_USERS
  - どのgithubアカウントに対してチェックを行うか
    - `\`区切り
- CHECK_STEPS
  - どれくらいの活動数で写真を切り替えるか
    - `\`区切り
  - 対応する画像をリモートに保存する
