# GitHub Actions

外部アクションの `uses:` は 40 桁のコミット SHA で固定し、末尾のコメントに対応するバージョンを記載する。

```yaml
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
```

タグ参照を追加したら、リポジトリのルートで [pinact](https://github.com/suzuki-shunsuke/pinact) を実行して固定する。

```sh
pinact run --verify-comment
pinact run --check --verify-comment
```

`main` などのブランチ参照は `pinact` の通常実行では固定されないため、使用するコミットと一致するタグがあるか確認する。
一致するタグがなければ、そのコミットの SHA に固定して元のブランチ名をコメントに残す。

依存の更新は `renovate.json5` の `helpers:pinGitHubActionDigestsToSemver` で管理する。
