from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import threading
import argparse
import re, subprocess
import cgi, tempfile
from ast import literal_eval
from gdeploylib import Helpers
import gdeploy

class LocalData(object):
    records = {}

class HTTPRequestHandler(BaseHTTPRequestHandler, Helpers):

    def do_POST(self):
        if None != re.search('/api/v1/addrecord/*', self.path):
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'application/json':
                length = int(self.headers.getheader('content-length'))
                data = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
                recordID = self.path.split('/')[-1]
                LocalData.records[recordID] = data
                print "record %s is added successfully" % recordID
            else:
                data = {}

            self.send_response(200)
            self.end_headers()
        elif None != re.search('/api/v1/rungdeploy/*', self.path):
            recordID = self.path.split('/')[-1]
            if LocalData.records.has_key(recordID):
                self.send_response(200)
                section = literal_eval(
                     LocalData.records[recordID].keys()[0])
                config_file = tempfile.mkstemp()[1]
                for key, value in section.iteritems():
                    self.write_config(key, value, config_file)
                command = 'gdeploy -c %s' % config_file
                subprocess.call(command.split(),
                        stdin=None, stdout=None, stderr=None, shell=False)
            else:
                 self.send_response(400, 'Bad Request: record does not exist')
                 self.send_header('Content-Type', 'application/json')
                 self.end_headers()
        else:
             self.send_response(403)
             self.send_header('Content-Type', 'application/json')
             self.end_headers()
        return


    def do_GET(self):
        if None != re.search('/api/v1/getrecord/*', self.path):
            recordID = self.path.split('/')[-1]
            if LocalData.records.has_key(recordID):
                 self.send_response(200)
                 self.send_header('Content-Type', 'application/json')
                 self.end_headers()
                 section = literal_eval(
                     LocalData.records[recordID].keys()[0])
                 self.wfile.write(section)
            else:
                 self.send_response(400, 'Bad Request: record does not exist')
                 self.send_header('Content-Type', 'application/json')
                 self.end_headers()
        else:
             self.send_response(403)
             self.send_header('Content-Type', 'application/json')
             self.end_headers()

        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)

class SimpleHttpServer():

    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip,port), HTTPRequestHandler)

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def waitForThread(self):
        self.server_thread.join()

    def addRecord(self, recordID, jsonEncodedRecord):
        LocalData.records[recordID] = jsonEncodedRecord

    def stop(self):
        self.server.shutdown()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='HTTP Server')
    parser.add_argument('port', type=int, help='Listening port for HTTP Server')
    parser.add_argument('ip', help='HTTP Server IP')
    args = parser.parse_args()

    server = SimpleHttpServer(args.ip, args.port)
    server.start()
    server.waitForThread()
    server.stop()
