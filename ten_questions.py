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

    return jsonify({"display": 'I have picked my secret word! Ask your first question... (questions remaining: %s)' % questions_remaining})

@app.route("/questions", methods=["POST"])
def questions():
    global questions_remaining
    question = request.json.get("question")
    print(question)            
    prompt = open_file('prompt_valid.txt').replace('<<QUESTION>>', question)
    is_valid = gpt_completion(prompt, temp=0.0)
    
    if is_valid == 'False':
        questions_remaining = questions_remaining - 1
        return jsonify({"display":'Wasted attempt! That is not a yes or no question!'})
    elif is_valid == 'True':
        questions_remaining = questions_remaining - 1
        prompt = open_file('prompt_answer.txt').replace('<<SECRET>>', secret_word).replace('<<QUESTION>>', question)
        answer = gpt_completion(prompt)
        if answer == 'Correct!':
            return jsonify({"display":'Congratulations! You won the game! The word was ' + secret_word})
        else:
            return jsonify({"display": answer})
    else:
        return jsonify({"display":'Sorry, the machine is confused, try again. No points deducted.'})

    
    if questions_remaining <= 0:
        return jsonify({"display":'You are out of guesses! The correct answer was: %s' % secret_word})
 


if __name__ == '__main__':
  """   # Choose difficulty
    difficulty_level = ""
    seed_words = ""
    while True:
        difficulty = input("Choose your difficulty (easy, medium, hard): %s" % difficulty_level.lower())
        if difficulty == "easy":
            seed_words = open_file('easy_words.txt').splitlines()
            break
        elif difficulty == "medium":
            seed_words = open_file('medium_words.txt').splitlines()
            break
        elif difficulty == "hard":
            seed_words = open_file('hard_words.txt').splitlines()
            break
        else:
            print("Sorry I didn't understand, please try again.")
            continue

    random.seed()
    secret_word = random.choice(seed_words)
    questions_remaining = 10
    hint_response = ""
    print('I have picked my secret word! Ask your first question... (questions remaining: %s)' % questions_remaining)

    
    while True:  
        if questions_remaining == 6 or questions_remaining == 3:
            while True:
                hint = input("Would you like a hint (yes or no)? %s" % hint_response.lower())
                if hint == "yes":
                    prompt = open_file('prompt_hint.txt').replace('<<WORD>>', secret_word)
                    hint_answer = gpt_completion(prompt)
                    if hint_answer is None:
                        print("Sorry, couldn't come up with a hint")
                    else:    
                        print(hint_answer)
                    break
                elif hint == "no":
                    print("No hint provided")
                    break
                else:
                    print("I didn't understand. Please try again")
                
        # user asks a question        
        question = input('Question (%s): ' % questions_remaining)
        prompt = open_file('prompt_valid.txt').replace('<<QUESTION>>', question)
        is_valid = gpt_completion(prompt, temp=0.0)
    
        if is_valid == 'False':
            print('Wasted attempt! That is not a yes or no question!')
        elif is_valid == 'True':
            prompt = open_file('prompt_answer.txt').replace('<<SECRET>>', secret_word).replace('<<QUESTION>>', question)
            answer = gpt_completion(prompt)
            if answer == 'Correct!':
                replay = ""
                print('Congratulations! You won the game! The word was ' + secret_word)
                while True:
                    play_again = input("Would you like to play again (yes/no)?  %s" % replay.lower())
                    if play_again == "yes":
                        os.execv(sys.executable, ['python', 'TenQuestions.py'])
                    elif play_again == "no":
                        print("Thanks for playing!")
                        exit(0)
                    else:
                        continue
            print(answer)    
        else:
            print('Sorry, the machine is confused, try again. No points deducted.')
            continue
        # check if user has lost
        questions_remaining = questions_remaining - 1
        if questions_remaining <= 0:
            replay = ""
            print('You are out of guesses! The correct answer was: %s' % secret_word)
            while True:
                play_again = input("Would you like to play again (yes/no)?  %s" % replay.lower())
                if play_again == "yes":
                    os.execv(sys.executable, ['python', 'TenQuestions.py'])
                elif play_again == "no":
                    print("Thanks for playing!")
                    exit(0)
                else:
                    continue"""

__name__ == '__main__' 