from flask import Flask, request, render_template
from wsgiref.simple_server import make_server
import configparser
import requests
import datetime
# 載入 json 標準函式庫，處理回傳的資料格式
import json

import os
ON_HEROKU = os.environ.get('ON_HEROKU')

from bs4 import BeautifulSoup

app = Flask(__name__)


# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

config = configparser.ConfigParser()
config.read('config.ini')
try:
    access_token = os.environ['channel_access_token']
    channel_secret = os.environ['channel_secret']
except:
    access_token = config.get("line-bot", "channel_access_token")
    channel_secret = config.get("line-bot", "channel_secret")

line_bot_api = LineBotApi(access_token)     # 確認 token 是否正確
handler = WebhookHandler(channel_secret)            # 確認 secret 是否正確


def exchangerate():
    url = "https://rate.bot.com.tw/xrt/flcsv/0/day"
    rate = requests.get(url)
    rate.encoding = 'utf-8'
    rt = rate.text
    rts = rt.split('\n')
    mes = str()
    for i in range(9):
        try:                             # 使用 try 避開最後一行的空白行
            a = rts[i].split(',')             # 每個項目用逗號拆分成子串列
            if i < 8:
                mes += str(a[0]) + ": " + str(a[12] + "\n")
            else:
                mes += str(a[0]) + ": " + str(a[12])
        except:
            break
    return(mes)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
    app.logger.info("Request body" + body)
    now = datetime.datetime.now()
    print(now.strftime("%H%M%S"))

    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
         
    except InvalidSignatureError:
        abort(400)
    return 'OK'                                              # 驗證 Webhook 使用，不能省略


@handler.add(MessageEvent, message=TextMessage)
def send_message(event):
    print(event.message.text)
    msg = cathy_exchange_rate()
    msg += str(event.source.user_id)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text = msg)
    )



def cathy_exchange_rate():
    url = 'https://www.cathaybk.com.tw/cathaybk/personal/product/deposit/currency-billboard/#currency'
    web = requests.get(url)
    soup = BeautifulSoup(web.text, "html.parser")
    country = soup.find_all('div', class_='cubre-m-currency__name')     # 取得所有 class 為 reservoir 的 tag

    rates = []
    for i in range(len(country)-1):
        rate = soup.find_all('tbody')[i].find_all('tr')[1].find_all('td')[2]
        rate = rate.find_next().get_text()
        rates.append(rate)

    msg = str()
    for i in range(3):
        msg += country[i].get_text().lstrip().strip()
        msg += ('\n')
        msg += "數位通路優惠匯率: "
        msg += rates[i].lstrip()
        if i < 2:
            msg += ('\n\n')
    return(msg)


if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 80)




