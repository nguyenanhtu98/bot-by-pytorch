import random
import json
import torch
import re
from multiwords import multiSentences
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
from sendNotice import sendNotice
from texttospeech import tts

device = torch.device('cpu')

with open('intents.json', 'r', encoding='utf-8', errors='ignore') as f:
    intents = json.load(f)

FILE = "data.pth"
data = torch.load(FILE)
btags = ""
bques = ""

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

def solve(msg):
    global btags
    global bques
    sentence = msg
    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(dtype=torch.float).to(device)
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents["intents"]:
            if tag == intent["tag"]:
                if tag not in btags:
                    btags += tag + " - "
                    response = random.choice(intent['responses'])
                    return (response) + "\n\n"
                else:
                    return ""
    else:
        if msg not in bques:
            bques += msg + " - "
            return msg + ": Mình tạm thời chưa có đáp án" + "\n\n"
        else:
            return ""

def getRes(mssg,voice):
    empt = "Mình tạm thời chưa có đáp án"
    bot_response = ""
    if type(multiSentences(mssg)) is str:
        bot_response += solve(mssg)
        if empt in solve(mssg):
            sendNotice(mssg)
    else:
        listmsg = multiSentences(mssg)
        if listmsg == []:
            bot_response += "Vậy bạn muốn biết về điều gì"
        else:
            for msg in listmsg:
                bot_response += solve(msg)
                if empt in solve(msg):
                   sendNotice(msg)
    global btags
    btags = ""
    global bques
    bques = ""
    bot_response = bot_response[:-2]
    bot_voice = re.sub(r'(https?://[^\s]+)','', bot_response)

    print(bot_response)
    if(voice == 1):
        tts(bot_voice)
    return bot_response

#msg = input('input: ')
getRes("system context diagram",0)