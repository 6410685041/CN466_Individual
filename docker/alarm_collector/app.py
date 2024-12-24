import paho.mqtt.client as mqttc
import time
import json
from utils.lineNotify import Notify_User
from utils.mongodb import insert_house_data

from dotenv import load_dotenv
load_dotenv()
import os

MQTT_BROKER ="mqtt.eclipseprojects.io"
MQTT_PORT = 1883
MQTT_SUB_TOPIC = "CN466/Alarm/house/#"

def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(MQTT_SUB_TOPIC)
        else:
            print("Failed to connect, return code %d\n", rc)
        
    def on_message(client, userdata, msg):
        topic = msg.topic
        payload = json.loads(msg.payload.decode('utf-8'))
        print("Create new document")
        home_id = topic.split("CN466/Alarm/house/")[-1]
        doc = {
            "timestamp" : payload["timestamp"],
            "home_id": home_id,
            "image" : payload["image"]
            }
        insert_house_data(doc)
        Notify_User(home_id)
            
    client = mqttc.Client(mqttc.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    return client

mqttClient = connect_mqtt()

while True:
    time.sleep(3)
    mqttClient.loop()