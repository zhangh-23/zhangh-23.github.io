import re
import os
import sys
import openai
import textwrap
from time import time,sleep
from pprint import pprint
from uuid import uuid4
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)
questions_remaining=10
hint_response = ""
secret_word =""

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

openai.api_key = open_file('openaiapikey.txt')


def gpt_completion(prompt, model='text-davinci-003', temp=1.2, top_p=1.0, tokens=100, freq_pen=0.0, pres_pen=0.0, stop=['\n', 'asdasdf']):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()  # force it to fix any unicode errors
    while True:
        try:
            response = openai.Completion.create(
                model=model,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            return text
        except Exception as e:
            retry += 1
            if retry >= max_retry:
                return "Error: %s" % e
            print('Error communicating with OpenAI:', e)
            sleep(1)


@app.route("/init", methods=["GET"])
def init():
    seed_words = ""
    global questions_remaining
    global secret_word
    args = request.args
    difficulty = args["level"].lower()
    
    if difficulty == "Easy":
        seed_words = open_file('easy_words.txt').splitlines()
    elif difficulty == "Medium":
        seed_words = open_file('medium_words.txt').splitlines()
    elif difficulty == "Hard":
        seed_words = open_file('hard_words.txt').splitlines()
    else:
        seed_words = open_file('easy_words.txt').splitlines()


    random.seed()
    secret_word = random.choice(seed_words)

    # secret_word = "cinema"

    return jsonify({"display": 'I have picked my secret word! Ask your question...'})

@app.route("/questions", methods=["POST"])
def questions():
    global questions_remaining
    global secret_word
    question = request.json.get("question")
               

    prompt = open_file('prompt_valid.txt').replace('<<QUESTION>>', question)
    # prompt = 'hint'
    # if prompt.lower() == 'hint':
    #     # print('here')
    #     hint_returned = hints()
    #     print("hint_returned", hint_returned)
    #     if hint_returned is None:
    #         return jsonify({"display":"Sorry, couldn't come up with a hint"})
    #     else:    
    #         return jsonify({"display":hint_returned})

    is_valid = gpt_completion(prompt, temp=0.0)
    
    if is_valid == 'False':
        questions_remaining = questions_remaining - 1
        return jsonify({"display":f'Wasted attempt! That is not a yes or no question!,(Attempts Left:{questions_remaining})'})
    elif is_valid == 'True':
        questions_remaining = questions_remaining - 1
        print(questions_remaining) 
        prompt = open_file('prompt_answer.txt').replace('<<SECRET>>', secret_word).replace('<<QUESTION>>', question)
        
       
        answer = gpt_completion(prompt)
        if answer == 'Correct!':
            return jsonify({"display":'Congratulations! You won the game! The word was ' + secret_word})
        else:
            response_data = {
            'display': f'''{answer},(Attempts Left:{questions_remaining})'''
            }
            return jsonify(json.loads(json.dumps(response_data)))
    else:
        return jsonify({"display":'Sorry, the machine is confused, try again. No points deducted.'})

    
    if questions_remaining <= 0:
        return jsonify({"display":'You are out of guesses! The correct answer was: %s' % secret_word})
 

# @app.route("/hints", methods=["GET"])
def hints():
    global secret_word
    # print('here')
    prompt = open_file('prompt_hint.txt').replace('<<WORD>>', secret_word)
    hint_answer = gpt_completion(prompt)
    print(hint_answer)
    return hint_answer
    
    
    


if __name__ == '__main__':
    __name__ == '__main__' 