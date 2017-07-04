import requests
from flask import Flask,request
import json

app=Flask(__name__)

PAT=""

@app.route("/b",methods=['POST'])
def get_response():
    req = request.get_data()
    print(req)

    for sender, message in messaging_events(req):
        print("Incoming from {}: {}".format(sender, message))
        #send_message(PAT, sender, message)
    return "ok"


def messaging_events(req):
  data = json.loads(req)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"


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

if __name__ == '__main__':
  app.run()