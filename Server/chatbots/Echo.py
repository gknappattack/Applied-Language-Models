from chatbots.Chatbot import Chatbot

class Echo(Chatbot):
    response = None
    def send_message(self):
        return self.response
    def recv_message(self, message):
        self.response = message
        return super().recv_message(message)