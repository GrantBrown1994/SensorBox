from time import sleep
from Adafruit_CCS811 import Adafruit_CCS811
import paho.mqtt.client as mqtt
import sys

ccs = Adafruit_CCS811()

username = "25476c20-af7d-11e7-bba6-6918eb39b85e"
password = "2c33743aed57caee5780d2252f9d9319d0d64bfe"
clientid = "e1a8cfd0-b018-11e7-bd7e-3193fab997a8"

mqttc = mqtt.Client(client_id=clientid)
mqttc.username_pw_set(username, password=password)
mqttc.connect("mqtt.mydevices.com", port=1883, keepalive=60)
mqttc.loop_start()

topic_CCS811_carbon = "v1/" + username + "/things/" + clientid + "/data/1"
topic_CCS811_TVOC = "v1/" + username + "/things/" + clientid + "/data/2"

sleep(10) #Sleep to allow wireless to connect before starting MQTT

while True:
	try:
		CO = ccs.geteCO2()
		TVOC = ccs.getTVOC()

		if not ccs.available():
			pass
		if ccs.available():
			temp = ccs.calculateTemperature()
			if not ccs.readData():
				if CO is not None:
					CO180 = "CO,Ppm=" + str(CO)
					mqttc.publish(topic_CCS811_carbon, payload =CO180, retain=True)
				if TVOC is not None:
					TVOC180 = "TVOC,Ppb=" + str(TVOC)
					mqttc.publish(topic_CCS811_TVOC, payload =TVOC180, retain=True)
		sleep(5)
	except (EOFError, SystemExit, KeyboardInterrupt):
        	mqttc.disconnect()
        	sys.exit()
