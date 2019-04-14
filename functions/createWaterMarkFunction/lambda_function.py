# -*- coding: utf-8 -*-
import os
import logging
import json
import urllib.request as request
import water_mark
import requests

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

    # この関数で生成した画像のイベントでないかチェック
    if is_slack_bot(event):
        logging.info("this is bot.")
        return "OK"    

    # ファイルかどうかのチェック
    if not is_file_created(event):
        return "OK"
        
    file_info = get_file_info(event)
    # 画像かどうかのチェック
    if not is_image(file_info):
        return "OK"
    
    resultPath = water_mark.create(file_info)

    # Slackにメッセージを投稿する
    post_image_to_channel('lambda-test', resultPath)

    return 'OK'

def post_image_to_channel(channel, resultPath):
    url = "https://slack.com/api/files.upload"
    headers = {
        "Content-Type": "multipart/form-data",
        "Authorization": "Bearer {0}".format(os.environ["SLACK_BOT_USER_ACCESS_TOKEN"])
    }
    # data = {
    #     "token": os.environ["SLACK_BOT_VERIFY_TOKEN"],
    #     "channels": channel,
    #     "text": message,
    #     "attachments": [{
    #         "fields": [
    #             {
    #                 "title": "てすと",
    #                 "value": "てすと",
    #             }],
    #         "image_url": "http://hogehoge/fuga.png"
    #     }]
    # }

    # req = request.Request(url, data=json.dumps(data).encode("utf-8"), method="POST", headers=headers)
    # request.urlopen(req)

    files = {'file': open(resultPath, 'rb')}
    param = {
        'token':os.environ["SLACK_BOT_USER_ACCESS_TOKEN"],
        'channels':channel,
        'initial_comment': "initial_comment",
        'title': "title",
    }
    logging.info(requests.post(url=url,params=param, files=files).content)

def is_verify_token(event):

    # トークンをチェック    
    token = event.get("token")
    if token != os.environ["SLACK_BOT_VERIFY_TOKEN"]:
        return False

    return True
    
def is_slack_bot(event):
    slackBotId = os.environ["SLACK_BOT_ID"]
    return event.get("event").get("user_id") == slackBotId

def is_file_created(event):
    return event.get("event").get("type") == "file_created"
    
def is_image(file_info):
    allowedFileFormat = [
            'jpg',
            'png',
            'gif'
        ]
    uploadedFileFormat = file_info.get('filetype')
    return uploadedFileFormat in allowedFileFormat
    
def get_file_info(event):
    filesInfoApi = "https://slack.com/api/files.info?token={token}&file={fileId}&pretty=1"
    fileId = event.get("event").get("file_id")
    token = os.environ["SLACK_BOT_USER_ACCESS_TOKEN"]
    
    # files.info APIにリクエストを投げる
    url = filesInfoApi.format(token=token, fileId=fileId)
    
    # 実際にAPIにリクエストを送信して結果を取得する
    response = request.urlopen(url)
    responseJson = json.loads(response.read().decode('utf8'))
    
    # 必要なのはfileオブジェクトのみ
    file_info = responseJson.get('file')
    return file_info