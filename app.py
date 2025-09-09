import os, requests, logging, time
from flask import Flask, request, abort, jsonify
from dotenv import load_dotenv
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.webhook import WebhookParser, MessageEvent
from linebot.v3.webhooks import TextMessageContent
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage

load_dotenv()
ACCESS_TOKEN=os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET=os.getenv("LINE_CHANNEL_SECRET")
OLLAMA_URL=os.getenv("OLLAMA_URL","http://localhost:11434")
MODEL=os.getenv("MODEL","qwen2.5:7b")
SYSTEM_PROMPT=os.getenv(
    "SYSTEM_PROMPT",
    "あなたは中学生に寄り添う優しい家庭教師です。専門用語を避け、やさしい言葉で、短い文で、3文以内で答えてください。例や手順は簡潔に。個人情報は聞かないでください。",
)
ENABLE_LOG = os.getenv("ENABLE_LOG", "false").lower() in ("1", "true", "yes", "on")

config=Configuration(access_token=ACCESS_TOKEN)
parser=WebhookParser(CHANNEL_SECRET)
app=Flask(__name__)
logging.basicConfig(
    level=(logging.INFO if ENABLE_LOG else logging.WARNING),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("linebot-lite")
if not ENABLE_LOG:
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

def ask_ollama(user_text):
    start = time.time()
    try:
        r=requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model":MODEL,
                "stream":False,
                "messages":[
                    {"role":"system","content":SYSTEM_PROMPT},
                    {"role":"user","content":user_text}
                ],
            },
            timeout=60,
        )
        r.raise_for_status()
        content = r.json().get("message",{}).get("content","(応答なし)")
        dur_ms = int((time.time()-start)*1000)
        if ENABLE_LOG:
            logger.info("ollama ok model=%s dur_ms=%s in_len=%s out_len=%s", MODEL, dur_ms, len(user_text), len(content))
        return content
    except Exception as e:
        if ENABLE_LOG:
            logger.exception("ollama failed")
        return f"(エラー: LLM応答に失敗しました: {e})"

@app.get("/healthz")
def healthz():
    return jsonify({"status":"ok"})

@app.route("/callback",methods=["POST"])
def callback():
    sig=request.headers.get("X-Line-Signature","")
    body=request.get_data(as_text=True)
    try:
        events=parser.parse(body,sig)
    except Exception:
        if ENABLE_LOG:
            logger.warning("invalid signature or payload")
        abort(400)
    if ENABLE_LOG:
        logger.info("webhook events=%s", len(events))
    with ApiClient(config) as client:
        api=MessagingApi(client)
        for e in events:
            if isinstance(e,MessageEvent) and isinstance(e.message,TextMessageContent):
                reply_text = ask_ollama(e.message.text)
                if reply_text is None:
                    reply_text = "(応答なし)"
                # LINEのテキスト上限は約2000文字
                reply_text = reply_text[:2000]
                api.reply_message(ReplyMessageRequest(
                    reply_token=e.reply_token,
                    messages=[TextMessage(text=reply_text)]
                ))
                if ENABLE_LOG:
                    logger.info("replied len=%s", len(reply_text))
    return "OK",200

if __name__=="__main__":
    app.run(host="0.0.0.0",port=8000)
