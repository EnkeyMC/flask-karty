from flask.ext.login import current_user
from src.data.models import User

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

def can_access (user):
    now = datetime.now().time()

    groups = user.group

    for g in groups:
        time_from = g.access_time_from
        time_to = g.access_time_to

        if time_from is not None or time_to is not None:
            print now
            print time_from
            print time_to

            if time_from < now < time_to:
                return True

    return False


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("device/+/ctecka/request", qos=0)
    client.subscribe("device/+/ctecka/log", qos=0)

def on_message(client, userdata, msg):

    print(msg.topic+": "+str(msg.payload))

    if(msg.topic.endswith("ctecka/request")):
        s = session()
        code = msg.payload
        user = User.find_by_number(code)
        before, sep, after = msg.topic.rpartition('/')
        #client.publish(before + sep + "potvrzeni", payload=ACCESS_ALLOWED_CODE)
        #print("ACCESS ALLOWED")
        if user and can_access(user):

            client.publish(before + sep + "potvrzeni", payload=ACCESS_ALLOWED_CODE)
            print("ACCESS ALLOWED")
            card = CardEntries(card_number=code, time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            s.add(card)
            s.commit()
        else:
            client.publish(before + sep + "potvrzeni", payload=ACCESS_DENIED_CODE)
            print("ACCESS DENIED")

        code = DEFAULT_CODE
        s.remove();
    elif (msg.topic.endswith("ctecka/log")):
        print msg.payload

Base = declarative_base()

engine = create_engine('mysql://root:root@localhost/karty')

session = sessionmaker()
session.configure(bind=engine, autocommit=True)
Base.metadata.create_all(engine)

#client = mqtt.Client(clean_session=False)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.1.97", 1883)
client.loop_forever()

