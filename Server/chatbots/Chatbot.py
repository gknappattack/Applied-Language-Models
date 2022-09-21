from datetime import datetime

class Chatbot():
    history = {}
    graph = None

    def __init__(self, history={}, graph=None):
        self.history = history
        self.graph = graph

    def get_history(self):
        return self.history
    
    def get_graph(self):
        return self.graph

    def send_message(self):
        pass

    def recv_message(self, message):
        msg_time = datetime.now()
        self.history[str(msg_time)] = message
