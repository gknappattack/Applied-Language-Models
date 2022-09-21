from chatbots.Chatbot import Chatbot
import classy_classification
import spacy
 
class Classy(Chatbot):
 
   def __init__(self):
       super().__init__()
       self.last_message = ""
       quests = open("chatbots/classy_files/quest.txt", "r")
       conversations = open("chatbots/classy_files/conversation.txt", "r")
       self.nlp = spacy.load("en_core_web_lg")
       data = {
           "quests": [line for line in quests],
           "conversation": [line for line in conversations]
       }
       self.nlp.add_pipe("text_categorizer",
           config={
               "data": data,
               "model": "spacy"
           }
       )
  
   def send_message(self):
       result = self.nlp(self.last_message)._.cats
       return {"text": str(result)}
 
   def recv_message(self, message):
       self.last_message = message["text"]
       return super().recv_message(message)
