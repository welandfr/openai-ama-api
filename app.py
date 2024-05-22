import os, json
import openai
from openai import OpenAI
from datetime import datetime
from flask import Flask, request
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

authorized_keys = (os.getenv("API_KEY", "") + "," + os.getenv("USER_KEYS", "")).split(",")
app.config['tokens_used'] = dict.fromkeys(authorized_keys, 0)
app.config['current_date'] = datetime.now().date()
model = os.environ.get("MODEL", "gpt-3.5-turbo")
max_tokens = os.environ.get("MAX_TOKENS", 500) # Max generated tokens

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

@app.route("/", methods=("GET", "POST"))
def index():

    api_key = request.args.get('api_key', None)

    if api_key not in authorized_keys or len(api_key.strip()) == 0:
        return { "msg": "Bad/no API_KEY provided"}, 401

    token_limit = int(os.getenv("TOKEN_LIMIT", 1000))

    if request.method == "POST":

        try: 
            # Throw error if request format not correct
            question = json.loads(request.data).strip()
        except:
            return { "msg": "Error: Bad request"}, 400

        # Reset used tokens for all users on first change of current_date
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
            response = client.chat.completions.create(
                model=model,
                messages=[ {"role": "user", "content": question} ],
                max_tokens=max_tokens
            )

        except openai.APIConnectionError as e:
            print("The server could not be reached")
            print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        except openai.RateLimitError as e:
            print("A 429 status code was received; we should back off a bit.")
        except openai.APIStatusError as e:
            print("Another non-200-range status code was received")
            print(e.status_code)
            print(e.response)
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
