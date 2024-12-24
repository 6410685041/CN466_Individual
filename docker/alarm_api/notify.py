import paho.mqtt.client as mqttc
import time
import json
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from utils.mongodb import mongo_home_by_id

from dotenv import load_dotenv
load_dotenv()
import os

MQTT_BROKER ="mqtt.eclipseprojects.io"
MQTT_PORT = 1883
MQTT_SUB_TOPIC = "Notify/Line"

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
notify_message = "Notification: There is visitor on your house\n check: https://liff.line.me/2006527696-Xkd3WNLr"

def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(MQTT_SUB_TOPIC)
        else:
            print("Failed to connect, return code %d\n", rc)
        
    def on_message(client, userdata, msg):
        payload = json.loads(msg.payload.decode('utf-8'))
        Notify_User(payload["home_id"])
                
    client = mqttc.Client(mqttc.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    return client

def Notify_User(home_id):
    home = mongo_home_by_id(home_id)
    if home!="[]":
        home = json.loads(home)[0]
        families = home["family"]
        for person in families:
            try:
                # Using the LineBotApi instance to send a text message
                line_bot_api.push_message(person, TextSendMessage(text=notify_message))
                print("Message sent successfully.")
            except LineBotApiError as e:
                # Error handling if something goes wrong
                print(f"Failed to send message: {e}")

mqttClient = connect_mqtt()

while True:
    time.sleep(3)
    mqttClient.loop()