import random

from chatbots.conversation.generators.duck_duck_go import DuckDuckGoResponseGenerator
from chatbots.conversation.generators.eliza import ElizaResponseGenerator
from chatbots.conversation.generators.greeter import GreeterResponseGenerator
from chatbots.conversation.generators.wiki_bot import WikiResponseGenerator
from chatbots.conversation.generators.ai21_bot import AI21ResponseGenerator

#from chatbots.conversation.generators.Trevor_Gen import TrevorResponseGenerator
#from chatbots.conversation.generators.ai21_bot import AI21ResponseGenerator
#from chatbots.conversation.generators.RhysandGenerator import RhysandGenerator
#from chatbots.conversation.generators.Don_Quarlos import DonQuarlosResponseGenerator

duckduckgo = DuckDuckGoResponseGenerator()
eliza = ElizaResponseGenerator()
greeter = GreeterResponseGenerator()
wiki = WikiResponseGenerator()
ai = AI21ResponseGenerator()

#bot = AI21ResponseGenerator()
#trevor = TrevorResponseGenerator()
#don_quarlos = DonQuarlosResponseGenerator()
#rhysand = RhysandGenerator()

response_generators = [duckduckgo, eliza, greeter, wiki, ai]

if __name__=="__main__":
    sample_texts = ["I'm having a bad day", "I feel so sad.", "Tell me about cats", "What is minecraft", "minecraft", "are you a robot", "I just want to die"]
    response_generators = [greeter]
    response = ""
    for g in response_generators:
        print('\n'+g.name())
        for t in sample_texts:
            g.input_data = {"previous_response":response,
                            "handpicked_keywords":[random.choice(t.split())],
                            "topic":'books',
                            "strict_topic":'books',
                            "ner": {},
                            "key_phrases":[random.choice(t.split())],
                            "text":t}
            response = g.response(t)['response']
            print('   '+response)
