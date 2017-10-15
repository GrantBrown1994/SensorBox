import paho.mqtt.client as mqtt
import time
import sys
import Adafruit_DHT as dht

time.sleep(30) #Sleep to allow wireless to connect before starting MQTT

username = "25476c20-af7d-11e7-bba6-6918eb39b85e"
password = "2c33743aed57caee5780d2252f9d9319d0d64bfe"
clientid = "e1a8cfd0-b018-11e7-bd7e-3193fab997a8"

mqttc = mqtt.Client(client_id=clientid)
mqttc.username_pw_set(username, password=password)
mqttc.connect("mqtt.mydevices.com", port=1883, keepalive=60)
mqttc.loop_start()

topic_dht22_temp = "v1/" + username + "/things/" + clientid + "/data/Temperature"
topic_dht22_humidity = "v1/" + username + "/things/" + clientid + "/data/Humidity"

while True:
    try:
        humidity22, temp22 = dht.read_retry(dht.DHT22, 4) #22 is the sensor type, 4 is the GPIO pin number (not physical pin number)
        if temp22 is not None:
            temp22 = "temp,c=" + str(temp22)
            mqttc.publish(topic_dht22_temp, payload=temp22, retain=True)
        if humidity22 is not None:
            humidity22 = "rel_hum,p=" + str(humidity22)
            mqttc.publish(topic_dht22_humidity, payload=humidity22, retain=True)
        time.sleep(5)
    except (EOFError, SystemExit, KeyboardInterrupt):
        mqttc.disconnect()
        sys.exit()
