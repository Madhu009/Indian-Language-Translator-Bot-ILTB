from flask import Flask, render_template,request
import json
from botinitializer import BotInitializer
from trainers import BotCorpusTrainer

app = Flask(__name__)

english_bot = BotInitializer("English Bot")
english_bot.set_trainer(BotCorpusTrainer)
english_bot.train("bot.corpus.punjabi")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get/<string:query>", methods=['POST'])
def get_raw_response(query):
    return str(english_bot.get_response(query))



@app.route("/get_response", methods=['POST'])
def get_raw_response_android():
    msg = request.json['msg']
    response,img=english_bot.get_response(msg)
    response=str(response)
    a = {"response": "yes", "msg": response,"image":img}
    json_data = json.dumps(a)
    return str(json_data)


@app.route("/get_data")
def get_data():
    msg=request.json
    print(msg)


if __name__ == "__main__":
    app.run()