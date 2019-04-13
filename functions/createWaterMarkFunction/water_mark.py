import os
import logging
import json
import urllib.request as request
from PIL import Image

def create(image_file_info):
    # logging.info(json.dumps(image_file_info))
    image_url = image_file_info.get('url_private_download')
    
    headers = {
        "Authorization": "Bearer {0}".format(os.environ["SLACK_BOT_USER_ACCESS_TOKEN"])
    }
    get_image_request = request.Request(image_url, None, headers)
    image_response = request.urlopen(get_image_request)
    
    image = image_response.read()
    
    im1 = Image.open(image)
    
    logging.info(im1)
    
    # with open(image_path, 'rb') as f:
    #     img = f.read()
    # # バイナリデータを指定してインスタンス生成
    # m = pymraw.Imagick(img)
    # logging.info(m)
    # pass