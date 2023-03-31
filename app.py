import os, json
import openai
from flask import Flask, request

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

TOKEN_QUOTA = 1000
app.config['tokens_used'] = 0

@app.route("/", methods=("GET", "POST"))
def index():
    if request.args.get('api_key', None) != os.getenv("API_KEY"):
        return { "msg": "Bad/no API_KEY provided"}, 401

    if request.method == "POST":

        question = json.loads(request.data)

        if request.args.get('simulation'):
            return { 
                'question': question,
                'answer': 'The answer is 42.',
                'model':'simulation',
                'tokens_cost': 0,
                'tokens_left': TOKEN_QUOTA-app.config['tokens_used']
            }
            
        if app.config['tokens_used'] > TOKEN_QUOTA: 
            return { "msg": f"TOKEN QUOTA EXCEEDED ({TOKEN_QUOTA})"}, 400
        
        try: 
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[ {"role": "user", "content": question} ]
            )

        except openai.error.AuthenticationError as e:
            return { "msg": f"OpenAI AuthenticationError: {e}"}, 401
        except Exception as e:
            return { "msg": f"OpenAI API returned an Error: {e}"}, 500

        app.config['tokens_used'] += response.usage.total_tokens

        return { 
            'question': question,
            'answer': response.choices[0].message.content,
            'model': response.model,
            'tokens_cost': response.usage.total_tokens,
            'tokens_left': TOKEN_QUOTA-app.config['tokens_used']
        }
    
    return { "msg": "USAGE: POST question as a JSON string."}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
