from linebot import LineBotApi
from linebot.exceptions import LineBotApiError

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage
)

import json
import os
from utils.mongodb import home_by_id

from dotenv import load_dotenv
load_dotenv()

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
configuration = Configuration(access_token=os.environ['CHANNEL_ACCESS_TOKEN'])
notify_message = "Notification: There is visitor on your house\n check: https://liff.line.me/2006527696-Xkd3WNLr"

def Notify_User(home_id):
    home = home_by_id(home_id)
    if home!="[]":
        home = json.loads(home)[0]
        families = home["family"]
        for person in families:
            try:
                push_message(person, notify_message)
                print("Message sent successfully.")
            except LineBotApiError as e:
                # Error handling if something goes wrong
                print(f"Failed to send message: {e}")

def push_message(user_id, message):
    try:
        # Configure the LINE Messaging API client
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            
            # Send the push message
            response = line_bot_api.push_message_with_http_info(
                PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=message)]
                )
            )
            print(f"Message sent to {user_id}, Response: {response}")
    except Exception as e:
        print(f"Error sending message to {user_id}: {e}")
