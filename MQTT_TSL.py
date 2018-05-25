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

topic_CCS811_full = "v1/" + username + "/things/" + clientid + "/data/3"
topic_CCS811_infared = "v1/" + username + "/things/" + clientid + "/data/4"
topic_CCS811_visible = "v1/" + username + "/things/" + clientid + "/data/5"

time.sleep(10) #Sleep to allow wireless to connect before starting MQTT

while True:
	try:
		# Get I2C bus
		bus = smbus.SMBus(1)

		# TSL2561 address, 0x39(57)
		# Select control register, 0x00(00) with command register, 0x80(128)
		#		0x03(03)	Power ON mode
		bus.write_byte_data(0x39, 0x00 | 0x80, 0x03)
		# TSL2561 address, 0x39(57)
		# Select timing register, 0x01(01) with command register, 0x80(128)
#		0x02(02)	Nominal integration time = 402ms
		bus.write_byte_data(0x39, 0x01 | 0x80, 0x02)

		time.sleep(0.5)

		# Read data back from 0x0C(12) with command register, 0x80(128), 2 bytes
		# ch0 LSB, ch0 MSB
		data = bus.read_i2c_block_data(0x39, 0x0C | 0x80, 2)
		# Read data back from 0x0E(14) with command register, 0x80(128), 2 bytes
		# ch1 LSB, ch1 MSB
		data1 = bus.read_i2c_block_data(0x39, 0x0E | 0x80, 2)

		# Convert the data
		ch0 = data[1] * 256 + data[0]
		ch1 = data1[1] * 256 + data1[0]
		ch2 = ch0 - ch1
		if ch0 is not None:
			FS180 = "Full Spectrum,Lux=" + str(ch0)
			mqttc.publish(topic_CCS811_full, payload =FS180, retain=True)
		if ch1 is not None:
			IS180 = "Infared Spectrum,Lux=" + str(ch1)
			mqttc.publish(topic_CCS811_infared, payload =IS180, retain=True)
		if ch2 is not None:
			VS180 = "Visible Spectrum,Lux=" + str(ch2)
			mqttc.publish(topic_CCS811_visible, payload =VS180, retain=True)
		time.sleep(5)

	except (EOFError, SystemExit, KeyboardInterrupt):
        	mqttc.disconnect()
        	sys.exit()

