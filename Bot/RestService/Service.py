from flask import Flask, render_template,request
import json
from botinitializer import BotInitializer
from trainers import BotCorpusTrainer
from PreProcessing import InputPreProcessor
app = Flask(__name__)

bot = BotInitializer("English Bot")
bot.set_trainer(BotCorpusTrainer)
bot.train("bot.corpus.punjabi")


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get/<string:query>", methods=['POST'])
def get_raw_response(query):
    return str(bot.get_response(query))



@app.route("/get_response", methods=['POST'])
def get_raw_response_android():
    msg = request.json['msg']

    #code for getting responses for every token
    ip=InputPreProcessor()
    tokens=ip.pre_process(msg)
    token_confidence=[]
    for token in tokens:
        token_confidence.append(bot.get_response(token))
    print(tokens)
    print(list(zip(tokens,token_confidence)))
    lang = request.json['lang']

    response,cofidence=bot.get_response(msg)
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