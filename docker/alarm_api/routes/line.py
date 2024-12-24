import os
from dotenv import load_dotenv
from utils.mongodb import mongo_home_by_id, mongo_insert_user, mongo_insert_home, mongo_find_user

load_dotenv()

from datetime import datetime 

from flask import request, abort, Blueprint
import json

from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import Profile

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

# Load environment variables
load_dotenv()

line_blueprint = Blueprint('line', __name__)

configuration = Configuration(access_token=os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])
line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])  # Correct initialization

@line_blueprint.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    reply_text = create_reply(event)

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

def create_reply(event):
    user_message = event.message.text
    user_id = event.source.user_id

    if user_message.startswith("#register"):
        # #command type home_id password
        command = user_message.split()[1]
        home_id = user_message.split()[2]
        password = user_message.split()[3]

        if command == "account":
            json_home = mongo_home_by_id(home_id)
            registered = mongo_find_user(user_id)
            if json_home!="[]":
                home = json.loads(json_home)[0]
                # # make sure that only home per user
                # if registered!="[]":
                #     reply_text = "The User Id is already registered."
                if password == home['password']:
                    user_data = {
                        'user_id': user_id,
                        'home_id': home_id
                    }
                    mongo_insert_user(user_data)
                    reply_text = f"The User Id is succesfully registered."
            reply_text = "Home Id is not existed or Password is wrong."

        elif command == "home":
            home = mongo_home_by_id(home_id)
            if home!="[]" :
                reply_text = f"{home_id} is already existed."
            else :
                if len(password)<5 or len(home_id)<5:
                    reply_text = "The password or home ID is too short."
                else:
                    home_data = {
                        'home_id': home_id,
                        'password': password,
                        'family': []
                    }
                    mongo_insert_home(home_data)
                    reply_text = "Home account is succesfully created."

    elif user_message == "#account":
        registered = mongo_find_user(user_id)
        if registered!="[]":
            home_registered = json.loads(registered)[0]['home_id']
            reply_text = f"This account is register to {home_registered}"
        else :
            reply_text = f"This account is not registered yet."

    elif user_message == "#check":
        reply_text = "link: https://liff.line.me/2006527696-Xkd3WNLr"

    else:
        reply_text = ("Command Manual:\n"
                "- To register house: #register home <your home id> <your home password> \n"
                "- To register user account in home: #register account <your home id> <your home password> \n"
                "- To check if user already register to home or not: #account \n"
                "- To check visitor: #check")

    return reply_text
