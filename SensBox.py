import HostTracker
import DBAggregator
import socket
import multiprocessing
import SocketServer
import netifaces
from Server import MyHandler
from SensorCollection import *
from time import sleep, gmtime, strftime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Session, engine, Base
import datetime
import os
from MQTT import MQTT


class SensNode:
    def __init__(self, name, headIP):
        netifaces.ifaddresses('eth0')
        ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
        self.node = HostTracker.Node(ip, name, "node")
        # HostTracker.helloWorld(headIP, self.node)

    def startNode(self):
        # server and data collection run in parallel
        cd = multiprocessing.Process(target=self.collectData())
        mqtt = multiprocessing.Process(target=MQTT())
        mqtt.start()
        cd.start()
        mqtt.join()
        cd.join()

    def collectData(self):
        # perpetually collects data from sensor
        # also calls addToTable()
        while True:
            FS, IS, VS = Light()
            CO, TVOC = Air()
            cTemp, fTemp, humidity = Temp()
            pressure = Pressure()
            self.addToTable(FS,IS,VS, CO, TVOC, cTemp, fTemp, humidity, pressure)
            sleep(10)

    def addToTable(self, FS, IS, VS, CO, TVOC, cTemp, fTemp, humidity, pressure):
        # adds collected data to local SQLite database using SQLAlchemy ORM
        # Base, Session, and engine are all defined in base.py
        # should be MySQL db of SensHost
        Base.metadata.create_all(engine)
        session = Session()
        new_reading = Readings(strftime("%Y-%m-%d %H:%M:%S", gmtime()), self.node.name, FS, IS, VS, CO, TVOC, cTemp, fTemp, humidity, pressure)
        session.add(new_reading)
        session.commit()
        session.close()


class SensHead(SensNode):
    def __init__(self, name):
        netifaces.ifaddresses('eth0')
        ip = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
        self.node = HostTracker.Node(ip, name, "head")
        self.hostList = HostTracker.HostList(self.node)
        self.hostList.newNode(self.node)
        self.aggregator = DBAggregator.DBAggregator(self.hostList)

    def startHead(self):
        # server, aggregator, and data collection run in parallel
        httpd = SocketServer.TCPServer(("", 8080), MyHandler)
        wb = multiprocessing.Process(target=httpd.serve_forever())
        cd = multiprocessing.Process(target=self.collectData())
        agg = multiprocessing.Process(target=self.aggregateData())
        mqtt = multiprocessing.Process(target=MQTT())
        mqtt.start()
        wb.start()
        cd.start()
        agg.start()
        mqtt.join()
        wb.join()
        cd.join()
        agg.join()

    def aggregateData(self):
        # in charge of timing for data aggregation
        # deletes aggregated data locally after upload to Remote
        self.aggregator.uploadDB()
        # while true:
        #     self.aggregator.updateList(self.hostList)
        #     self.aggregator.runSCP()
        #     self.aggregator.combineDB()
        #     self.aggregator.uploadDB()
        #     sleep(300)
        #     cmd = os.popen("rm -r /dbAgg/")
        #     cmd.read()
