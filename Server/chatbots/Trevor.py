from chatbots.Chatbot import Chatbot
import json

class Trevor(Chatbot):
    response = None
    def send_message(self):
        return {"text": "Plr->4:I am Trevor Ashby"}
    def recv_message(self, message):
        self.response = message
        return super().recv_message(message)