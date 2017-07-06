import requests
from flask import Flask, render_template,request
import json
from botinitializer import BotInitializer
from trainers import BotCorpusTrainer
from PreProcessing import InputPreProcessor
app = Flask(__name__)

bot = BotInitializer("English Bot")
bot.set_trainer(BotCorpusTrainer)
bot.train("bot.corpus.punjabi")


PAT="EAAYX07LLHJwBAMwzWwfrVZCDw2VP6AfH13zreLfiqMLOle5dq9fXkzsHZBiy7vZAthB2MNuy2VsoI0rKqQP1UQoF2HMLOpNTFC5YSHKqKZBrolkxzASjsgh9dGQP03HZBajskfJEgjZCGsBstDhAzLIEM8bOaKHMzxXLpoPB4j9QZDZD"


@app.route("/",methods=['POST'])
def get_response():
    req = request.get_data()
    print(req)

    for sender, message in messaging_events(req):
        print("Incoming from {}: {}".format(sender, message))

        response, cofidence = bot.get_response(message.decode('unicode_escape'))
        response = str(response)
        print(response)

        '''if message=="GrmEQkfhEgZCeZ":
            send_error_message(PAT, sender, "error.. Try again!")
        else:
            send_message(PAT, sender, message)'''

    return response


@app.route('/', methods=['GET'])
def handle_verification():
  print ("Handling Verification.")
  if request.args.get('hub.verify_token', '') == 'token_verified':
    print ("Verification successful!")
    return request.args.get('hub.challenge', '')
  else:
    print ("Verification failed!")
    return 'Error, wrong validation token'

def messaging_events(req):
  data = json.loads(req)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"] \
            and "attachments" not in event["message"] and "sticker_id" not in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "GrmEQkfhEgZCeZ"



def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print(r.text)

def send_error_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print(r.text)

if __name__ == '__main__':
  app.run()