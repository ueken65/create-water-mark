import os
import logging
import json
import urllib.request as request
# from PIL import Image

def create(imageFileInfo):
    # logging.info(json.dumps(image_file_info))
    imageUrl = imageFileInfo.get('url_private_download')

    headers = {
        "Authorization": "Bearer {0}".format(os.environ["SLACK_BOT_USER_ACCESS_TOKEN"])
    }

    getImageRequest = request.Request(imageUrl, None, headers)
    targetImage = request.urlopen(getImageRequest).read()
    tmpPath = '/tmp/target'
    resultPath = '/tmp/result.' + imageFileInfo.get('filetype')
    with open(tmpPath, mode="wb") as f:
        f.write(targetImage)

    logging.info(os.system('convert -composite ' + tmpPath+ ' img/mochiya_wm.png ' + resultPath))
    return resultPath