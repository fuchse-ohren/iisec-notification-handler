# 利用方法
## リポジトリをクローン
```
$ git clone https://github.com/fuchse-ohren/iisec-notification-handler
$ cd iisec-notification-handler
```

## `docker-compose.yml`を編集
```
$ vim docker-compose.yml
```

```
IISEC_ID: "" # IDを入力
IISEC_PW: "" # パスワードを入力
MODEL_PATH: "./model/tinyswallow-1.5b-instruct-q8_0.gguf"
DISCORD_WEBHOOK:  # DiscordのWebhook URLを入力
SLACK_WEBHOOK: # SlackのWebhook URLを入力
NOT_BEFORE_ID: # 現在最新の記事IDを入力すると，それ以前の記事の取得をスキップできます
```

## コンテナの立ち上げ
```
$ docker-compose up
```
