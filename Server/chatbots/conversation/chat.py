import sys

from graph import KnowledgeGraph
from byu_eve import conversation_engine


ce = conversation_engine()
kn = KnowledgeGraph()
stored = ""

response = ce.start()
print()
while(1):
    text = input(response+'\n')
    stored += text
    kn.plot(stored)
    response = ce.chat(text, verbose=True)
