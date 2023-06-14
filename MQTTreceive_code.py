from paho.mqtt import client as mqtt
import base64
import time
import pathlib
from queue import Queue
imgpath = 'C:/Users/chrispower/OttoCam Captures/'
broker = 'mqtt.eclipseprojects.io'
#'broker.hivemq.com'
port = 1883
topic = 'camPhotos'
q = Queue()
client=mqtt.Client()

 
def on_connect(client, userInfo, flags, rc):
    if rc == 0:
        print('Established connection successully!')

def on_message(client, userInfo, message):
    print("New Image Received")  
    q.put(message)
    if message.payload == 0 or message.payload == "":
        print("No Data received")  
    
  

client.on_connect=on_connect
client.on_message=on_message
client.connect(broker, port)
client.subscribe(topic)
client.loop_start
while not q.empty():
    message = q.get()
    if message is None:
        print("There was an error in opening the image file.")
        continue
    print(message)
    msg = str(message.payload.decode('utf-8'))
    img = msg.encode('ascii')
    full_img = base64.b64decode(img)
    currtime = time.strftime('%Y%m%d-%H%M%S')
    saveimg = imgpath + str(currtime) + '.jpg'
    open(saveimg, "wb").write(full_img + '.jpg')
client.loop_forever()



