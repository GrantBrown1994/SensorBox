import os
import sqlite3
import requests
from SensorCollection import Readings, ReadingsCombined, ReadingsRemote
from base import BaseRemote, engineRemote, SessionRemote, BaseCombined, engineCombined, SessionCombined


class DBAggregator:
    # undecided if each SensNode will have a local SQLite or if host will have one master MySQL
    def __init__(self, hostList):
        self.hostList = hostList
        self.directoryFrom = "db/db.db"
        self.directoryTo = "dbAgg/"

    def updateList(self, hostList):
        # ensures that the aggregator has the most up to date list of SensNodes in the network
        self.hostList = hostList

    def runSCP(self):
        # collects SQLite databases from nodes and stores them in head
        # sends http put request to each node after database is fetched in order to delete them
        user = "pi"
        a = 0
        for i in self.hostList:
            a += 1
            cmd = os.popen('scp ' + user + '@' + i.ipAddress + ':' + self.directoryFrom + ' ' + self.directoryTo + "db" + str(a) + ".db")
            cmd.read()
            payload = {'directory': self.directoryFrom}
            requests.put(i.ipAddress, payload)

    def combineDB(self):
        # concatenates collected SQLite databases into one large database
        con3 = sqlite3.connect(self.directoryTo + "combine.db")
        for filename in os.listdir(self.directoryTo):
            con3.execute("ATTACH \'" + filename + "\' as dba")

            con3.execute("BEGIN")
            for row in con3.execute("SELECT * FROM dba.sqlite_master WHERE type='table'"):
                combine = "INSERT INTO " + row[1] + " SELECT * FROM dba." + row[1]
                print(combine)
                con3.execute(combine)
            con3.commit()
            con3.execute("detach database dba")
        self.organizeDB()

    def organizeDB(self):
        # organizes concatenated database by DateTime field
        con3 = sqlite3.connect(self.directoryTo + "combine.db")
        con3.execute("select *  from Table order  by datetime(datetimeColumn) DESC LIMIT 1")
        con3.commit()

    def uploadDB(self):
        # uploads MySQL database to Remote cloud server
        # uses ORM to ensure the databases can communicate with each other

        # create the local db
        BaseCombined.metadata.create_all(engineCombined)
        sessionCombined = SessionCombined()

        # create the Remote db and start the session
        BaseRemote.metadata.create_all(engineRemote)
        sessionRemote = SessionRemote()

        for reading in sessionCombined.query(ReadingsCombined):
            # reading is already attached to a session, so a tmp variable must be created to avoid conflicts
            tmp = ReadingsRemote(reading.time, reading.box_name, reading.FS, reading.IS, reading.VS, reading.CO, reading.TVOC,
                           reading.cTemp, reading.fTemp, reading.humidity, reading.pressure)
            sessionRemote.add(tmp)

        # commit changes and close the session
        sessionRemote.commit()
        sessionRemote.close()
