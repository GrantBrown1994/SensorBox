import requests
import subprocess


class HostList:
    def __init__(self, node):
        # routingTable is to be an array of Nodes containing the name
        # and IP address of each node as well as its parent/child status
        # tableDirectory contains routingTable information
        # headNode is frequently accessed so it makes sense to keep a more accessible copy
        self.routingTable = []
        self.headNode = node
        self.tableDirectory = "table.txt"

    def setHead(self):
        # searches routingTable for head node
        # should only need to run on head node change
        found = 0
        for n in self.routingTable:
            if n.status == "head":
                self.headNode = n
                found = 1
                break
        if found == 0:
            print("Error 1: No head found")
            exit(1)

    def newNode(self, node):
        # rudimentary way to add nodes
        # error checking needs to be implemented
        self.routingTable.append(node)
        f = open(self.tableDirectory, "a+")
        f.write("%s %s %s\n" % (node.ipAddress, node.name, node.status))
        f.close()

    def updateTable(self):
        with open(self.tableDirectory, "r") as ins:
            for line in ins:
                self.tableDirectory.append(line.split())


def helloWorld(ip, node):
    # send http get request to head node
    # delivers ip and name as payload
    # node status is assumed
    payload = {'name': node.name, 'ipAddress': node.ipAddress}
    try:
        requests.get(ip, params=payload)
    except requests.exceptions.ConnectionError as e:
        print e


class Node:
    def __init__(self, ipAddress=0, name=0, status=0):
        self.ipAddress = ipAddress
        self.name = name
        self.status = status
