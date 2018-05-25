import smbus
import time
import paho.mqtt.client as mqtt
import sys

username = "25476c20-af7d-11e7-bba6-6918eb39b85e"
password = "2c33743aed57caee5780d2252f9d9319d0d64bfe"
clientid = "e1a8cfd0-b018-11e7-bd7e-3193fab997a8"

mqttc = mqtt.Client(client_id=clientid)
mqttc.username_pw_set(username, password=password)
mqttc.connect("mqtt.mydevices.com", port=1883, keepalive=60)
mqttc.loop_start()

topic_sht31_fahr = "v1/" + username + "/things/" + clientid + "/data/6"
topic_sht31_celcius = "v1/" + username + "/things/" + clientid + "/data/7"
topic_sht31_humidity = "v1/" + username + "/things/" + clientid + "/data/8"


time.sleep(10) #Sleep to allow wireless to connect before starting MQTT

while True:
	try:
		# Get I2C bus
		bus = smbus.SMBus(1)

		# SHT31 address, 0x44(68)
		bus.write_i2c_block_data(0x44, 0x2C, [0x06])

		time.sleep(0.5)

		# SHT31 address, 0x44(68)
		# Read data back from 0x00(00), 6 bytes
		# Temp MSB, Temp LSB, Temp CRC, Humididty MSB, Humidity LSB, Humidity CRC
		data = bus.read_i2c_block_data(0x44, 0x00, 6)

		# Convert the data
		temp = data[0] * 256 + data[1]
		cTemp = -45 + (175 * temp / 65535.0)
		fTemp = -49 + (315 * temp / 65535.0)
		humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

		if fTemp is not None:
			fTemp180 = "temp,F=" + str(fTemp)
			mqttc.publish(topic_sht31_fahr, payload =fTemp180, retain=True)
		if fTemp is not None:
			cTemp180 = "temp,C=" + str(cTemp)
			mqttc.publish(topic_sht31_celcius, payload =cTemp180, retain=True)
		if fTemp is not None:
			humidity180 = "rel_hum,%= " + str(humidity)
			mqttc.publish(topic_sht31_humidity, payload =humidity180, retain=True)
		time.sleep(5)

	except (EOFError, SystemExit, KeyboardInterrupt):
        	mqttc.disconnect()
        	sys.exit()

