import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler
import HostTracker
import os


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # accepts http get request and parses payload
        # calls welcomeBrother()
        hostList =  HostTracker.HostList(HostTracker.Node())
        name = lambda ch: ch not in "[']", urlparse.parse_qs(urlparse.urlparse(self.path).query).get('name', None)
        ip = lambda ch: ch not in "[']", urlparse.parse_qs(urlparse.urlparse(self.path).query).get('ipAddress', None)
        hostList.newNode(HostTracker.Node(ip, name, "node"))

    def do_POST(self):
        # accepts http post request
        # calls updateTable()
        HostTracker.HostList.updateTable(HostTracker.HostList())

    def do_PUT(self):
        # deletes old SQLite databases
        directory = urlparse.parse_qs(urlparse.urlparse(self.path).query).get('directory', None)
        cmd = os.popen("rm " + directory)
        cmd.read()
