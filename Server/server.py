import json
import socket
from datetime import datetime
from chatbots.Echo import Echo
from chatbots.Gary import Gary
from chatbots.Trevor import Trevor
from chatbots.Kevin import Kevin
from chatbots.Chat import Chat
from chatbots.Classy import Classy
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer


chatbots = ["ECHO", "GARY", "TREVOR", "KEVIN", "CHAT"]
echo = Echo()
gary = Gary()
trevor = Trevor()
kevin = Kevin()
chat = Chat()
classy = Classy()

class GP(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def send_json(self, chatbot, json_input):
        chatbot.recv_message(json_input)
        data = chatbot.send_message() 
        data_json = json.dumps(data)
        self._set_headers()
        self.wfile.write(bytes(data_json, "utf-8"))
    def send_json_message(self, json_input):
        data_json = json.dumps(json_input)
        self._set_headers()
        self.wfile.write(bytes(data_json, "utf-8"))
    def do_HEAD(self):
        self._set_headers()
    def do_GET(self):
        self._set_headers()
    def do_POST(self):
        if self.path == "/":
            self._set_headers()
            root_text = "Currently no implementation at the base level.. \n Please try: /chatbot/<chatbotID or chatbotNAME>"
            data = {"text":root_text}
            self.send_json_message(data)
        elif self.path == "/chatbot" or self.path == "/chatbot/":
            data = {"text":"current list of chatbots", "chatbots":chatbots}
            self.send_json_message(data)
        elif self.path == "/chatbot/echo":
            print("Echo sent a message @: ", str(datetime.now()))
            req_json = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self.send_json(echo, req_json)
        elif self.path == "/chatbot/gary":
            print("Gary sent a message @: ", str(datetime.now()))
            req_json = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self.send_json(gary, req_json)
        elif self.path == "/chatbot/trevor":
            print("Trevor sent a message @: ", str(datetime.now()))
            req_json = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self.send_json(trevor, req_json)  
        elif self.path == "/chatbot/kevin":
            print("Kevin sent a message @: ", str(datetime.now()))
            req_json = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self.send_json(kevin, req_json)
        elif self.path == "/chatbot/chat":
            print("Chat sent a message @: ", str(datetime.now()))
            req_json = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self.send_json(chat, req_json)        
        elif self.path == "/chatbot/classy":
            print("Classy sent a message @: ", str(datetime.now()))
            req_json = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self.send_json(classy, req_json) 
        
# WYRMLING DEFAULT: 127.0.1.1:8088

def run(server_class=HTTPServer, handler_class=GP, port=8088):
    server_address = (socket.gethostbyname(socket.gethostname()), port)
    httpd = server_class(server_address, handler_class)
    print('Server running at {}:{}...'.format(socket.gethostbyname(socket.gethostname()), port))
    httpd.serve_forever()

run()