from src.data.models import Card

__author__ = 'Martin Omacht'

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from src.data.models.cardentries import CardEntries
import paho.mqtt.client as mqtt
from datetime import datetime

# CONSTANTS
DEFAULT_CODE = "00000000"

ACCESS_DENIED_CODE = "0"
ACCESS_ALLOWED_CODE = "1"

code = DEFAULT_CODE

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("ctecka", qos=0)

def on_message(client, userdata, msg):

    print(msg.topic+": "+str(msg.payload))

    if(msg.topic == "ctecka"):
        code = msg.payload

        if Card.find_by_number(code):
            client.publish("potvrzeni", payload=ACCESS_ALLOWED_CODE)
            print("ACCESS ALLOWED")
            now = datetime.now()
            card = CardEntries(card_number=code, time=now.strftime("%Y-%m-%d %H:%M:%S"))
            s.add(card)
            s.commit()
        else:
            client.publish("potvrzeni", payload=ACCESS_DENIED_CODE)
            print("ACCESS DENIED")

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

