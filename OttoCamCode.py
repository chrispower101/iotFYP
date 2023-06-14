from picamera import PiCamera
import time
from gpiozero import Button
from paho.mqtt import client as mqtt_client
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import smtplib
import base64
#email attachment libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


#setting up MQTT communication
broker = 'mqtt.eclipseprojects.io'

port = 1883
topic = "camPhotos"
clientID = "otto@raspberrypi"

#setting up PiCamera and configuring Rpi board settings
camera = PiCamera()
camera.resolution = (640, 480)
imgpath = '/home/chrispower/Desktop/captures/'
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) #set to use physical pin numbering

#LED settings
GPIO.setup(18, GPIO.OUT, initial=GPIO.HIGH) #set the pin 18 as output and make sure when it initialises it is set to HIGH aka ON)
GPIO.output(18, GPIO.HIGH)

#Button settings
button = Button(17)

#declaring email variables
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
USERNAME = '1olympuseye@gmail.com'  #the address used by the smart doorbell to send email notifications
PASSWORD = '**********' #typically a randonmly generated key given by google to recognise automatic sign in attempts from the smart doorbell as a verif user

def publish(client, image):
    with open(image, "rb") as image:

        imgData = image.read()
        
        base64_bytes = base64.b64encode(imgData)
        base64_msg = base64_bytes.decode('ascii')
        print(base64_msg)
        client.publish(topic, base64_msg)
    #msg_status = product[0]
    #if msg_status == 0:
        #print(f"Message sent to topic {topic}")
    #else:
        #print(f"Failed to send message to topic {topic}")
##Error handling and checks can be implemented here to verify a message being successfully posted




#class used for sending emails
class Emails:
    def sendEmail(self, rec, sub, cont, img):
        
        #HEADERS
        emailData = MIMEMultipart()
        emailData['Subject'] = sub
        emailData['To'] = rec
        emailData['From'] = USERNAME
        
        #Attach text data
        emailData.attach(MIMEText(cont))
        
        #Create .img data from defined img so it doesnt send as .dat file
        imageData = MIMEImage(open(img, 'rb').read(), 'jpg')
        imageData.add_header('Content-Disposition', 'attachment; filename="image.jpg"')
        emailData.attach(imageData)
        
        #CONNECT TO GMAIL SERVER
        sesh = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        sesh.ehlo()
        sesh.starttls()
        sesh.ehlo
        
        #LOGIN TO GMAIL
        sesh.login(USERNAME, PASSWORD)
        
        #SEND EMAIL
        sesh.sendmail(USERNAME, rec, emailData.as_string())
        sesh.quit

def main():
    client=mqtt.Client()
    client.connect(broker, port)
    client.subscribe(topic)
    sender = Emails()
    while True:
        
        button.wait_for_press()
            
        #camera.start_preview()
        camera.rotation = 180
        currtime = time.strftime('%Y%m%d-%H%M%S')
        img = imgpath + str(currtime) + '.jpg'
        GPIO.output(18, GPIO.LOW)
        time.sleep(1)
        GPIO.output(18, GPIO.HIGH)
        time.sleep(1)
        camera.capture(img) #capture image using picam
        #camera.close()
        #MQTT image transfer
        
        publish(client, img)
        time.sleep(1)
        
        GPIO.output(18, GPIO.LOW)
        sendTo = "********" #email address of recipient user
        #worth noting a doc containing list of multi recipients can be used for robustness and scalability, but security concerns must be addressed
        emailSub = "Someone's at the door!"
        emailCont = "Someone recently rang your doorbell at: " + time.ctime()
        sender.sendEmail(sendTo, emailSub, emailCont, img)
        time.sleep(1)
        GPIO.output(18, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(18, GPIO.LOW)
        time.sleep(1)
        GPIO.output(18, GPIO.HIGH)

        #camera.stop_preview()
        print("Image Taken! Email Sent.")

if __name__ == "__main__":
    main()