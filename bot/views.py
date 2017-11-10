# -*- encoding: utf-8 -*-
import json
import requests
import sys
import pya3rt
from django.http import HttpResponse
from linebot import LineBotApi
from PIL import Image
from io import BytesIO

sys.path.append('./bot')

REPLY_ENDPOINT = 'https://api.line.me/v2/bot/message/reply'
ACCESS_TOKEN = 'AgijaoZBHPotJEPMcY863vT14yfwK+s/10DUYEMX/d5HDeaGkH8uwS7WPse2Qf2T+G6V7TGCLBROjZDWMe62SxjevtvfpaDBHtVm8OOrkP/G2AUIVB5KWagAlBrvmTdK99LCUgzDDzvRA4HSNAZBMwdB04t89/1O/w1cDnyilFU='
HEADER = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + ACCESS_TOKEN
}
lINE_BOT_API = LineBotApi(ACCESS_TOKEN)

# recuitAPI
recuitapikey = "bcF8ridXk7nqTKRe9ZtFTKXZcIQs62NU"
client = pya3rt.TalkClient(recuitapikey)

# docomoAPI
docomoapikey = '595672394b51707248724e326146706c7938514d6545704843456b4774524f3344706e546a497032797134'

# Get API_Path
def __build_url(name, version='v1'):
    return __api_path.format({'version': version, 'name': name})

__api_path = 'https://api.apigw.smt.docomo.ne.jp/imageRecognition/{0[version]}/{0[name]}'


def index(request):
    return HttpResponse("This is bot api.")

    # Reply text
def reply_text(reply_token, rep_meg):
    payload = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": rep_meg
            }
        ]
    }

    requests.post(REPLY_ENDPOINT, headers=HEADER, data=json.dumps(payload))  # to send data to LINE
    return rep_meg


    # Save image
def save_image(messegeid):
    message_content = lINE_BOT_API.get_message_content(messegeid)

    i = Image.open(BytesIO(message_content.content))
    filename = '/tmp/' + messegeid + '.jpg'
    i.save(filename)

    return filename

    # Get json
def get_json(filename):
    with open(filename, mode='rb') as f:
        result = requests.post(
            url=__build_url('recognize'),
            params={'APIKEY': docomoapikey, 'recog': 'product-all', 'numOfCandidates': 5},
            data=f,
            headers={'Content-Type': 'application/octet-stream'})
        result.raise_for_status()
        result = result.json()
    return result

    # Reply carousel
def post_carousel(reply_token,imageUrl,title,brand,releaseDate,maker,url,itmeName):
    payload = {
          "replyToken":reply_token,
          "messages":[
              {
                "type": "template",
                "altText": "商品結果",
                "template": {
                    "type": "carousel",
                    "columns": [

                        {
                          "thumbnailImageUrl": imageUrl[0],
                          "title": itmeName[0],
                          "text": "ブランド名：" + brand[0] + " メーカー名："+ maker[0] +" 発売日：" +releaseDate[0],
                          "actions": [

                              {
                                  "type": "uri",
                                  "label": "Amazonで見る",
                                  "uri": url[0]
                              }
                          ]
                        },
                        {
                          "thumbnailImageUrl": imageUrl[1],
                          "title": itmeName[1],
                          "text": "ブランド名：" + brand[1] + " メーカー名："+ maker[1] +" 発売日：" +releaseDate[1],
                          "actions": [

                              {
                                  "type": "uri",
                                  "label": "Amazonで見る",
                                  "uri": url[1]
                              }
                          ]
                        },
                        {
                          "thumbnailImageUrl": imageUrl[2],
                          "title": itmeName[2],
                          "text": "ブランド名：" + brand[2] + " メーカー名："+ maker[2] +" 発売日：" +releaseDate[2],
                          "actions": [

                              {
                                  "type": "uri",
                                  "label": "Amazonで見る",
                                  "uri": url[2]
                              }
                          ]
                        }
                      ]
                }
              }
            ]
    }
    req = requests.post(REPLY_ENDPOINT, headers=HEADER, data=json.dumps(payload))
    return title[0]


def callback(request):
    reply = ""
    request_json = json.loads(request.body.decode('utf-8'))  # to get json

    for e in request_json['events']:
        reply_token = e['replyToken']  # to get reply_token
        message_type = e['message']['type']  # to get type

        # reply for test
        if message_type == 'text':
            text = e['message']['text']  # to get message
            rep_meg = client.talk(text)["results"][0]["reply"]  # to get reply message by recuitTalk
            reply += reply_text(reply_token, rep_meg)

            # reply for image
        if message_type == 'image':
            messegeid = e['message']['id']  # to get messageID
            filename = save_image(messegeid)
            result = get_json(filename)

            if (result.get('candidates') != None):
              imageUrl,title,brand,releaseDate,maker,url,itemName =[],[],[],[],[],[],[]

              for i in range(0,3): # to get item info
                imageUrl.append(result['candidates'][i]['imageUrl'])
                title.append(result['candidates'][i]['sites'][0]['title'])
                brand.append(result['candidates'][i]['detail']['brand'])
                releaseDate.append(result['candidates'][i]['detail']['releaseDate'])
                maker.append(result['candidates'][0]['detail']['maker'])
                url.append(result['candidates'][i]['sites'][0]['url'])
                itemName.append(result['candidates'][i]['detail']['itemName'][0:29]) # to restrict length

              reply += post_carousel(reply_token,imageUrl,title,brand,releaseDate,maker,url,itemName)

            else:
                rep_meg = "お探しのものは見つかりませんでした。"
                reply += reply_text(reply_token, rep_meg)

    return HttpResponse(reply)  # for test

