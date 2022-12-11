from flask import Flask, request
import ProcessedUpdate

app = Flask(__name__)

@app.post("/")
def process_update():

    # TODO: (Future updates) Use this logic to determine tile colours
    # print(type(data))
    # string = data['message']['text']
    # print(string)
    # for char in string:
    #     print(char + str(ord(char)))

    update = request.json
    #ASSUMPTION: this is any type of update object: https://core.telegram.org/bots/webhooks#testing-your-bot-with-updates
    processed_update  = ProcessedUpdate(update)

    print(vars(process_update))
    return "Welcome to the app"