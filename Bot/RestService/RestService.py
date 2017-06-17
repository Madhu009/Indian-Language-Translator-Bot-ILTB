from flask import Flask, render_template,request
import json
from botinitializer import BotInitializer
from trainers import BotCorpusTrainer

app = Flask(__name__)

bot = BotInitializer("English Bot")
bot.set_trainer(BotCorpusTrainer)
bot.train("bot.corpus.english")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get/<string:query>", methods=['POST'])
def get_raw_response(query):
    return str(bot.get_response(query))



@app.route("/get_response", methods=['POST'])
def get_raw_response_android():
    msg = request.json['msg']
    print(msg)
    response=bot.get_response(msg)
    response=str(response)
    a = {"response": "yes", "msg": response}
    json_data = json.dumps(a)
    return str(json_data)


@app.route("/get_data",methods=['POST'])
def get_data():
    msg=request.json
    print(msg)
    return "hi"


if __name__ == "__main__":
    app.run()