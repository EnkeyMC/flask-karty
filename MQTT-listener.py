__author__ = 'Martin Omacht'

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from src.data.models.carddata import Card
import paho.mqtt.client as mqtt
from datetime import datetime

# CONSTANTS
DEFAULT_CODE = "00000000"

ERROR_CODE = "0"
OK_CODE = "1"

code = DEFAULT_CODE

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("ctecka", qos=0)
    client.subscribe("outTopic", qos=0)

def on_message(client, userdata, msg):

    print(msg.topic+" "+str(msg.payload))

    if(msg.topic == "ctecka"):
        code = msg.payload
        if code == "00a20659":
            client.publish("potvrzeni", payload=ERROR_CODE)
            print("ERROR")
        else:
            client.publish("potvrzeni", payload=OK_CODE)
            print("OK")

        now = datetime.now()
        card = Card(card_number="0x" + code, time=now.strftime("%Y-%m-%d %H:%M:%S"))
        print card.time
        s.add(card)
        s.commit()

        code = DEFAULT_CODE

Base = declarative_base()

engine = create_engine('mysql://root:root@localhost/karty')

session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)

s = session()

#client = mqtt.Client(clean_session=False)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost")
client.loop_forever()

