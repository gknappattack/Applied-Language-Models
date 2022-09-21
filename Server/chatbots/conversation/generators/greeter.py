import random
from chatbots.conversation.generators.response_generator_base_class import ResponseGenerator

#-------------------------------------------------------
# This module opens (and perhaps also closes) conversations
# in a natural way that is customized to the individual

class GreeterResponseGenerator(ResponseGenerator):

    def name(self):
        return "greeter"

    def __init__(self):

        self.opening_lines = ["Hi there, how's it going?", "Hello, my name is Eve, and I like to talk about books.", "Hello, how can I help you?", "Hello, how are you feeling today?"]
        #self.opening_lines = ["Are you comfortable sharing your first name with me?", "How are you today?", "I can chat about music, literature, and politics."]
        #self.opening_lines = ["I can chat about sports, movies, and music.", "How are you today?", "What would you like to chat about?"]
        #self.opening_lines = ["I like to talk about movies, actors, and directors", "I can chat about movies, books, and other topics.", "How are you today?","How can I help you?","I enjoy chatting about movies.","I like books and music.","What would you like to talk about?"]
        #self.opening_lines = ["I can chat about movies, books, and other topics.", "How are you today?","How can I help you?","I like books and movies.","I like to talk about movies, actors, and famous people.", "I like to chat about sports, news, and politics."]
        
        # IF USER IS RETURNING AGAIN...
        #self.opening_lines = ["Nice to see you again.", "What's your name?","How's it going?"]
        #self.opening_lines = ["Hello again.", "What's your name?", "How may I serve you?", "How are you today?","What would you like to chat about?","I like to talk about movies, actors, and famous people.","I can chat about movies, books, and other topics.","I can chat about sports, news, and politics.","Greetings, Sensei."]
        #self.opening_lines = ["How's it going?","How are you today?","Are you comfortable sharing your first name with me?","May I ask your name?","What would you like to chat about?","I like to talk about movies, actors, and famous people.","I can chat about movies, books, and other topics."]
        #self.opening_lines = ["Hello again.", "Nice to see you again.", "I'm glad you're back.", "I can chat about sports, news, and politics.", "I can chat about Pokemon, Minecraft, and Star Wars.", "What's your name?"]

        #BEST ONES FOUND
        #self.opening_lines = ["How's it going?","Are you comfortable sharing your first name with me?","I like to talk about movies, actors, and famous people."]

    def response(self, text=None):

        return {'response': random.choice(self.opening_lines)}
