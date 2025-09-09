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
