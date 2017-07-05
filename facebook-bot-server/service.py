import requests
from flask import Flask,request
import json

app=Flask(__name__)

PAT="EAAYX07LLHJwBAEFmDTAZBVPh7XSkJ4mB5xGfIUfX73DIYJ0FLLyfFR3opTWZAnEOEt4wBlRebt6yLgzcIrd635CrUTwXW4POXoa7GmG0pHjwoQZAuD3pRpZBNzL5c5orZAolZBfrO7fEYQ1RaMYrktZAEyZB50yAiKD9jYE4uT03nwZDZD"


@app.route("/",methods=['POST'])
def get_response():
    req = request.get_data()
    print(req)

    for sender, message in messaging_events(req):
        print("Incoming from {}: {}".format(sender, message))
        send_message(PAT, sender, message)
    return "ok"


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