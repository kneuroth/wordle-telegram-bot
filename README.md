# Wordle Bot

> Telegram Wordle Bot documentation

## INITIALIZATION

> Info to initialize project, TODO: Dockerize these eventually 

### All Environments

In project root directory run: 

1. `$ python3 -m venv venv`
2. `$ source venv/bin/activate`
3. `$ pip install -r requirements.txt`
4. `$ pip install -r dev-requirements.txt`
5. `$ pip install -e .`
6. `$ flask run`

### Development


### Testing

**ENV** will be an environment variable in a .env file. Options are *DEV*, *TEST*, and *PROD*.

##### update_validation
Import requests json into Postman to test is_valid_signup_message and is_valid_score_submission

**CHAT_ID** will be an environment variable set in a .env file. For test.env the chat ID will be *-123456*.

**SIGNUP_PHRASE** will also be an environment variable set in a .env file, most likely "*/sign me up*".



#### Telegram Bot Information
>Use the telegram app and engage a chat with "botfather" to create a bot

>Generate a token and use this endpoint: 
`https://api.telegram.org/bot<token>/METHOD_NAME`
>
>Eg. `https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/getMe`
>
> Methods are documented in [telegram documentation](https://core.telegram.org/bots/api#making-requests)


>Use the setWebhook method to define the webhook URL and to set up a filter for allowed updates
>Eg. `https://api.telegram.org/bot123456:ACB-DEF1234ghlk-CQ/setWebhook`
>
>body:
>
>allowed_updates: ["message"]
>
>url: http://url-of-flask-app.com


### Running with docker

Make sure you delete the database and scoreboard before building

docker build -t wordle_bot_image .

docker run --rm --name wordle_bot_container -p 80:8000 wordle_bot_image export ENVIRONMENT=dev

To run with https enabled on the Compute VM Instance run:

(first make sure to move the cert and key files into the repo root directory)

docker run --rm --name wordle_bot_container -p 80:443 --env ENVIRONMENT=prod wordle_bot_image 

