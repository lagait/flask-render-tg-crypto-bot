import os
import requests
from flask import Flask, request, Response

app = Flask(__name__)

# Set up Telegram bot API
TELEGRAM_API_TOKEN = os.environ['BOT_TOKEN']
user_chat_id = os.environ['CHANNEL_ID']
telegram_api_url = f'https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage'

@app.route('/')
def hello():
    return 'Service for sending notifications to a telegram channel '

@app.route('/notify', methods=['POST', 'GET'])
def notify():
    logs = request.json
    if len(logs) == 0:
        print("Empty logs array received, skipping")
    else:
        print(logs)

        category = ""
        try:
            category = logs['event']['activity'][0]['category']
        except:
            print("category not defined")

        if logs['webhookId'] == os.environ['ALCHEMY_KEY'] and category == 'token':
            # extract the necessary information
            txhash = logs['event']['activity'][0]['hash']
            from_address = logs['event']['activity'][0]['fromAddress']
            to_address = logs['event']['activity'][0]['toAddress']
            token_symbol = logs['event']['activity'][0]['asset']
            token_address = logs['event']['activity'][0]['rawContract']['address']
            value = str(round(logs['event']['activity'][0]['value']))

            # create the text string
            message = f'*Token transfer:*\n[Link to Transaction](https://etherscan.io/tx/{txhash})\nfrom [{from_address}](https://etherscan.io/address/{from_address}#tokentxns)\nto [{to_address}](https://etherscan.io/address/{to_address}#tokentxns):\nvalue: {value} *{token_symbol}* [{token_address}](https://etherscan.io/address/{token_address})'

            # Send the message using HTTP request
            payload = {
                'chat_id': user_chat_id,
                'text': message,
                'parse_mode': 'MarkdownV2'
            }
            response = requests.post(telegram_api_url, json=payload)
            if response.status_code == 200:
                print('Message sent successfully.')
            else:
                print(f'Failed to send message. Status code: {response.status_code}')

    return Response(status=200)

if __name__ == '__main__':
    app.run()
