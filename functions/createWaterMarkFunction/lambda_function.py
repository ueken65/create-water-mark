# -*- coding: utf-8 -*-
import os
import logging
import json
import urllib.request as request
import water_mark

# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    # 受信データをCloud Watchログに出力
    logging.info(json.dumps(event))

    # SlackのEvent APIの認証
    if "challenge" in event:
        return event["challenge"]
    
    # tokenのチェック
    if not is_verify_token(event):
        return "OK"    
    
    # ファイルかどうかのチェック
    if not is_file_created(event):
        return "OK"
        
    file_info = get_file_info(event)
    # 画像かどうかのチェック
    if not is_image(file_info):
        return "OK"
    
    water_mark.create(file_info)
    # return_image = water_mark.create(file_info)
    # Slackにメッセージを投稿する
    post_message_to_channel(event.get("event").get("channel"), "Hello, Slack Bot!")

    return 'OK'

def post_message_to_channel(channel, message):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": "Bearer {0}".format(os.environ["SLACK_BOT_USER_ACCESS_TOKEN"])
    }
    data = {
        "token": os.environ["SLACK_BOT_VERIFY_TOKEN"],
        "channel": channel,
        "text": message,
    }

    req = request.Request(url, data=json.dumps(data).encode("utf-8"), method="POST", headers=headers)
    request.urlopen(req)

def is_verify_token(event):

    # トークンをチェック    
    token = event.get("token")
    if token != os.environ["SLACK_BOT_VERIFY_TOKEN"]:
        return False

    return True
    
def is_file_created(event):
    return event.get("event").get("type") == "file_created"
    
def is_image(file_info):
    allowed_file_format = [
            'jpg',
            'png',
            'gif'
        ]
    uploaded_file_format = file_info.get('filetype')
    return uploaded_file_format in allowed_file_format
    
def get_file_info(event):
    files_info_api = "https://slack.com/api/files.info?token={token}&file={file_id}&pretty=1"
    file_id = event.get("event").get("file_id")
    token = os.environ["SLACK_BOT_USER_ACCESS_TOKEN"]
    
    # files.info APIにリクエストを投げる
    url = files_info_api.format(token=token, file_id=file_id)
    
    # 実際にAPIにリクエストを送信して結果を取得する
    response = request.urlopen(url)
    response_json = json.loads(response.read().decode('utf8'))
    
    # 必要なのはfileオブジェクトのみ
    file_info = response_json.get('file')
    return file_info