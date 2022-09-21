from chatbots.Chatbot import Chatbot
from chatbots.conversation.byu_eve import conversation_engine
import json

class Chat(Chatbot):
    def __init__(self):
        self.response = None
        self.response_generator = conversation_engine()

    def send_message(self):
        prompt = self.response['text']

        print("Message from client: ", prompt)

        # Get response from conversation_engine
        convo_out = self.response_generator.chat(prompt, verbose=True)

        print("Output from eve: ", convo_out)

        return {'text': convo_out}

    def recv_message(self, message):
        self.response = message
        return super().recv_message(message)