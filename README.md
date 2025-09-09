# linebot-lite

このプロジェクトとREADMEは Codex が作成しました。

最小構成の LINE × Flask × Ollama のサンプルです。やさしい言葉で短く返す設定が既定です。

## クイックスタート（コピペ用）

1) アプリ起動

```
cd linebot-lite
source .venv/bin/activate
python app.py
```

2) ngrok を開始（別ターミナル）

```
ngrok http 8000
# Webhook URL:
# https://<ngrokドメイン>/callback
```

3) Ollama の稼働確認（どれか1つでOK）

```
ollama list
curl -s http://localhost:11434/api/version
curl -s http://localhost:11434/api/tags
# 未起動なら: ollama serve
```

## セットアップ

- Python 仮想環境
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install -U pip`
  - `pip install flask line-bot-sdk requests python-dotenv`

- 環境変数（.env）
  - `cp .env.example .env`
  - `.env` に以下を設定
    - `LINE_CHANNEL_ACCESS_TOKEN`
    - `LINE_CHANNEL_SECRET`
    - （必要なら）`MODEL` や `SYSTEM_PROMPT`

- 起動
  - `python app.py`
  - ヘルス: `curl http://127.0.0.1:8000/healthz`

## Webhook 設定

- `ngrok http 8000`
- LINE Developers → Messaging API → Webhook URL: `https://<ngrokドメイン>/callback`
- Verify → Use webhook: ON

## ふるまい（プライバシー/語調）

- ログ: 既定でOFF（`ENABLE_LOG=false`）。個人情報を含む内容は記録しません。
- 有効化したい場合のみ `.env` に `ENABLE_LOG=true` を設定。
- 語調: 既定の `SYSTEM_PROMPT` は「中学生向け・やさしい・短い返事」。必要に応じて `.env` で調整できます。

<!-- GitHub 公開手順はREADMEから削除（チャットで案内） -->
## 使い方

1) `.env` を準備
   - `cp .env.example .env` → `LINE_CHANNEL_ACCESS_TOKEN` と `LINE_CHANNEL_SECRET` を入力
   - 必要なら `MODEL` や `SYSTEM_PROMPT` を変更（既定は中学生向け）

2) アプリを起動
   - `python app.py`（ヘルス: `curl http://127.0.0.1:8000/healthz`）

3) ngrok を開始
   - `ngrok http 8000`（表示された https のURLを使います）

4) LINE の Webhook 設定
   - Webhook URL: `https://<ngrokドメイン>/callback` → Verify → Use webhook: ON → 応答モードは「Bot」

5) 動作確認
   - 友だち追加 → メッセージ送信 → ボットが返信（Ollamaの応答）

ヒント
- モデル変更: `.env` の `MODEL` を変えてアプリ再起動
- ログ切替: `.env` の `ENABLE_LOG` を `true/false`（既定はOFF）
- Ollama 稼働: `ollama serve`（既に起動中なら不要）

## n8n × Docker（練習用・無料）

最短で「ローカルDockerのn8n → ngrokで公開」を試す手順です。クラウド契約は不要です。

1) 起動（Docker必須）

```
docker compose up -d
open http://localhost:5678
```

2) n8nでワークフロー作成
- Webhook Trigger: Method=POST, Path=`line`
- （まずは疎通確認用）Respond to Webhookで`{{$json}}`を返す→Activate

3) ローカル動作確認

```
curl -X POST http://localhost:5678/webhook/line \
  -H 'Content-Type: application/json' \
  -d '{"events":[{"message":{"text":"hello"},"replyToken":"dummy"}]}'
```

4) 外部公開（任意）

```
ngrok http 5678
# LINE Webhook URL: https://<ngrokドメイン>/webhook/line
```

5) LINE連携（本番化する場合）
- Webhook → HTTP Request(Ollama) → HTTP Request(LINE返信)
- 署名検証（HMAC-SHA256）は必要に応じてFunctionノードで追加

### すぐ使える完成ワークフロー（インポート）

- ファイル: `workflows/n8n-line-ollama.json`
- 内容: LINE署名検証 → Ollama呼び出し → LINE返信 → Webhookに200/400で応答
- 使い方:
  1. n8n画面右上「Import from File」→ `workflows/n8n-line-ollama.json` を指定
  2. Webhookノードを開き、`Path`が`line`になっていることを確認（URLは`/webhook/line`）
  3. 必要な環境変数を`.env`に設定（docker-composeが読み込む）
     - `LINE_CHANNEL_ACCESS_TOKEN`
     - `LINE_CHANNEL_SECRET`
     - `OLLAMA_URL`（例: `http://localhost:11434`）
     - `MODEL`（例: `qwen2.5:7b`）
     - `SYSTEM_PROMPT`（任意）
  4. ワークフローをActivate
  5. 動作確認: `curl -X POST http://localhost:5678/webhook/line -H 'Content-Type: application/json' -d '{"events":[{"message":{"text":"hello"},"replyToken":"dummy"}]}'`
  6. 公開する場合: `ngrok http 5678` → LINEのWebhook URLを `https://<ngrok>/webhook/line` に設定

ヒント
- 署名検証エラー時は`400`で `{ ok:false, error:'invalid signature' }` を返します
- Webhookノードは「Options → Raw Body = ON」に設定済み（署名検証で使用）
- LINE返信テキストは2000文字に切り詰めています
