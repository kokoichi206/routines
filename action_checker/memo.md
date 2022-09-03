## urllib.request で返されるエラー

``` sh
# URL は正しいが、ラズパイが停止してるなどで届かない時
urllib.error.URLError: <urlopen error [Errno 101] Network is unreachable>

# そもそも URL がおかしい時
urllib.error.URLError: <urlopen error [Errno 8] nodename nor servname provided, or not known>
```
