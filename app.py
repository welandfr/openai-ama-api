import os, json

import openai
from flask import Flask, request, jsonify

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

TOKEN_QUOTA = 100
app.config['tokens_used'] = 0

@app.route("/", methods=("GET", "POST"))
def index():
    if request.args.get('api_key', None) != os.getenv("API_KEY"):
        return "ERROR: Bad/no API_KEY provided"

    if request.method == "POST":
        
        if app.config['tokens_used'] > TOKEN_QUOTA: 
            return f"TOKEN QUOTA EXCEEDED ({TOKEN_QUOTA})"

        question = json.loads(request.data)
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": question} ]
        )

        app.config['tokens_used'] += response.usage.total_tokens

        return { 
            'question': question,
            'answer': response.choices[0].message.content,
            'model': response.model,
            'tokens_cost': response.usage.total_tokens,
            'tokens_left': TOKEN_QUOTA-app.config['tokens_used']
        }
    
    return "USAGE: POST question as a JSON string."


