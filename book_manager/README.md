# Book Manager

Python 3.12 で Google Drive の書籍情報を取得し、Notion に未登録の項目を追加する。
Chrome と Selenium は使用しない。

## Google Drive

フォルダ直下にある、名前が `.pdf` で終わるファイルを取得する。サブフォルダは再帰しない。
タイトルはファイル名、URL は `https://drive.google.com/file/d/<id>/view?usp=sharing` とし、
Notion の既存項目との比較に使用する。API のページ送りで全件取得する。

### OAuth の初期設定・再認可

Google Cloud で Drive API が有効なプロジェクトのデスクトップ用 OAuth クライアントを用意する。
既存クライアントも使用できる。ダウンロードしたクライアント JSON はリポジトリ外へ保存する。

```sh
cd book_manager
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-auth.txt
mkdir -p ~/.config/routines/book-manager
chmod 700 ~/.config/routines/book-manager
python scripts/authorize_drive.py \
  ~/.config/routines/book-manager/client.json \
  ~/.config/routines/book-manager/oauth.json
```

Google の同意画面で取得する権限は `drive.metadata.readonly`。
この権限は Drive 全体のメタデータ読み取りを許可し、コード上の対象は指定フォルダに限定する。
ファイル本文の取得や Drive への書き込みは行わない。
出力 JSON は OAuth クライアント ID・シークレット・refresh token を含み、権限 `600` で保存する。
定期実行では `google-auth` が access token を自動更新する。refresh token が失効したら再認可し、Secret を更新する。
OAuth 同意画面の公開ステータスが Testing の場合は、[Google の制約](https://developers.google.com/identity/protocols/oauth2#expiration)で refresh token が 7 日後に失効するため、定期運用には Production を使用する。

### ローカル実行

```sh
export GOOGLE_DRIVE_FOLDER_ID='1PgVnNQDEFcxhDF4vOYLo-5mzL4731rPY'
export GOOGLE_DRIVE_OAUTH_JSON="$(cat ~/.config/routines/book-manager/oauth.json)"
export DATABASE_ID='your-notion-database-id'
export NOTION_API_SECRET='your-notion-api-key'
python main.py
```

`GOOGLE_DRIVE_FOLDER_ID` は環境変数を優先し、未指定なら `config/google_drive_config.py` を使用する。
`GOOGLE_DRIVE_OAUTH_JSON` は必須。実行に必要な依存関係だけを導入する場合は `pip install -r requirements.txt` を使用する。

### GitHub Actions

`production` Environment に以下の Secrets を登録する。
`DATABASE_ID` と `NOTION_API_SECRET` は既存の Repository Secrets も使用できる。

| Secret | 内容 |
| --- | --- |
| `GOOGLE_DRIVE_FOLDER_ID` | 取得対象のフォルダ ID |
| `GOOGLE_DRIVE_OAUTH_JSON` | 認可スクリプトが出力した JSON 全体 |
| `DATABASE_ID` | Notion のデータベース ID |
| `NOTION_API_SECRET` | Notion の API キー |

```sh
gh secret set GOOGLE_DRIVE_FOLDER_ID --repo kokoichi206/routines --env production \
  --body '1PgVnNQDEFcxhDF4vOYLo-5mzL4731rPY'
gh secret set GOOGLE_DRIVE_OAUTH_JSON --repo kokoichi206/routines --env production \
  < ~/.config/routines/book-manager/oauth.json
```

従来の `GOOGLE_DRIVE_URL` は使用しない。

### フォルダを今回だけ追加登録する

手動実行の `one_time_folder_ids` に、追加フォルダ ID を空白区切りで指定する。
追加分は直下の全ファイルを登録し、フォルダ自体とサブフォルダ内は対象にしない。
未指定の定期実行では、通常の books フォルダの `.pdf` だけを同期する。

`dry_run` を有効にすると、Notion の既存項目と比較して登録予定件数だけを出力する。
書き込み後は Notion を読み直し、取得元の全項目が存在することを確認する。
登録失敗や読み直し時の欠落はジョブの失敗として扱う。
同じ Notion データベースへ同時に登録しないよう、ワークフローの実行を直列化する。

```sh
gh workflow run update-books-info.yml --repo kokoichi206/routines \\
  --ref fix/books-drive-oauth \\
  -f one_time_folder_ids='1qQqHew3niLBkqeVR5P079qOKbVHMAr2- 18i6J6uHhpTR2bBmpg6k8FYYuZbX227GQ' \\
  -f dry_run=true
```

登録予定件数の確認後、`dry_run=false` で実行すると登録する。
ローカルでは `ONE_TIME_DRIVE_FOLDER_IDS` と `BOOK_MANAGER_DRY_RUN=true` で同じ処理を指定できる。
Notion が `429` または `529` を返した場合は `Retry-After` に従って最大 3 回再試行する。

## Notion

`DATABASE_ID` と `NOTION_API_SECRET` は環境変数を優先し、未指定なら `config/notion_config.py` を使用する。
タイトルと URL の両方が一致する項目は登録済みとして扱う。Drive から削除された本でも、Notion の既存項目は削除しない。
