import os, json
import openai
from datetime import datetime
from flask import Flask, request
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")
authorized_keys = (os.getenv("API_KEY", "") + "," + os.getenv("USER_KEYS", "")).split(",")
app.config['tokens_used'] = dict.fromkeys(authorized_keys, 0)
app.config['current_date'] = datetime.now().date()

@app.route("/", methods=("GET", "POST"))
def index():

    api_key = request.args.get('api_key', None)

    if api_key not in authorized_keys:
        return { "msg": "Bad/no API_KEY provided"}, 401

    token_limit = int(os.getenv("TOKEN_LIMIT", 1000))

    if request.method == "POST":

        try: 
            question = json.loads(request.data)
        except:
            return { "msg": "Error: Bad JSON"}, 400

        # Reset used tokens for all users on first day change
        if app.config['current_date'] != datetime.now().date():
            app.config['tokens_used'] = dict.fromkeys(authorized_keys, 0)
            app.config['current_date'] = datetime.now().date()

        # Return simulated response 
        if request.args.get('simulation'):
            return { 
                'question': question,
                'answer': 'The answer is 42.',
                'model':'simulation',
                'tokens_cost': 0,
                'tokens_left': token_limit-app.config['tokens_used'][api_key]
            }
            
        if app.config['tokens_used'][request.args.get('api_key')] > token_limit: 
            return { "msg": "Error: Token limit exceeded."}, 400
        
        # Do the OpenAPI request
        try: 
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[ {"role": "user", "content": question} ]
            )

        except openai.error.AuthenticationError as e:
            return { "msg": f"OpenAI AuthenticationError: {e}"}, 401
        except Exception as e:
            return { "msg": f"OpenAI API returned an Error: {e}"}, 500

        # Only increase token count for normal users
        if api_key != os.getenv("API_KEY"):
            app.config['tokens_used'][api_key] += response.usage.total_tokens

        return { 
            'question': question,
            'answer': response.choices[0].message.content,
            'model': response.model,
            'tokens_cost': response.usage.total_tokens,
            'tokens_left': token_limit-app.config['tokens_used'][api_key]
        }
    
    return { "msg": "USAGE: POST question as a JSON string."}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
