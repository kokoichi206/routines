## urllib.request で返されるエラー

``` sh
# URL は正しいが、ラズパイが停止してるなどで届かない時
urllib.error.URLError: <urlopen error [Errno 101] Network is unreachable>

# そもそも URL がおかしい時
urllib.error.URLError: <urlopen error [Errno 8] nodename nor servname provided, or not known>
```

## 行いたい処理

### ラズパイが止まっている時

gh-actions 自体が失敗したわけではないので、actions の実行結果としては問題なしを返したい。

そして、画像取得のみが失敗という扱いにし、デフォルトの画像を返す。

### 画像が見つからない時

設定値を間違える等で、誤った画像を指定した場合には画像取得が失敗する。

その時はデフォルトの画像を返したい。

### 上記以外のエラー

基本は想定してないエラーのはずなので、gh-actions 自体の実行結果としても失敗させる。

失敗したことを LINE で通知する。
