# OpenAPI Ask-Me-Anything pass-through API
### Fredrik Welander

## Usage:

- Create `.env` (from `.env.example`) and add you keys
- Send requests as a simple JSON string

### REQUEST:

```
POST http://localhost:8080?api_key=my-secret-key
Content-Type: application/json

"What are you?"

```
### RESPONSE:

```
{
  "answer": "I am an AI language model created by OpenAI designed to generate human-like responses to various prompts and tasks.",
  "model": "gpt-3.5-turbo-0301",
  "question": "What are you?",
  "tokens_cost": 34,
  "tokens_left": 966
}
```


