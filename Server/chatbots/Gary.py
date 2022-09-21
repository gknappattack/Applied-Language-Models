import spacy
import re
import numpy as np
from sklearn.linear_model import LogisticRegression
from transformers import pipeline
from chatbots.Chatbot import Chatbot

def make_classifier(nlp):
    classes = ['person', 'place', 'group', 'object', 'other']
    train_set = [
        ['Magni', 'Lady', 'ambassador', 'venomhide', 'George', 'Sargeras', 'Champion',
         'demon', 'Magni', 'Bronzebeard', 'Ogar', 'Chromie', 'Lord'],
        ['Azeroth', 'world', 'Orgrimmar', 'Spire'],
        ['Champions', 'adventurers', 'Alliance', 'spirits', 'elven', 'Blackmaw'],
        ['apple', 'owl', 'house', 'writ', 'sword', 'cloak', 'stones', 'ices', 'Waygate'],
        ['Assist', 'by', 'completing', '4', 'Azerite', 'quests',
         'The', 'Our', 'has', 'cut', 'deep', 'Her', 'pain', 'is', 
         'drivin', 'elements', 'into', 'a', 'frenzy', 'I', 'can', 
         'hear', 'voice', '-', 'battle', 'Doublecross', 'Drape', 'Don', 
         'eastern', 'undamaged', 'menace', 'summon', 'fighter', 'remedy', 'vilest', 'vilified',
         'banquet', 'group','entourage',
        ]
    ]
    X = np.stack([list(nlp(w))[0].vector for part in train_set for w in part])
    y = [label for label, part in enumerate(train_set) for _ in part]
    return classes, LogisticRegression(C=0.1, class_weight='balanced').fit(X, y)

def classifier_templater(line):
    print("Loading spacy model...")
    nlp = spacy.load("en_core_web_lg")
    classes, classifier = make_classifier(nlp)
    doc = nlp(line[:-1])
    num_people = 0
    num_places = 0
    num_groups = 0
    num_objects = 0
    for token in doc:
        classification = classes[classifier.predict([token.vector])[0]]
        if classification == 'person':
            compiled = re.compile(re.escape(token.text), re.IGNORECASE)
            line = compiled.sub(f"<PERSON {num_people}>", line)
            num_people += 1
        elif classification == 'place':
            compiled = re.compile(re.escape(token.text), re.IGNORECASE)
            line = compiled.sub(f"<PLACE {num_places}>", line)
            num_places += 1
        elif classification == 'group':
            compiled = re.compile(re.escape(token.text), re.IGNORECASE)
            line = compiled.sub(f"<GROUP {num_groups}>", line)
            num_groups += 1
        elif classification == 'object':
            compiled = re.compile(re.escape(token.text), re.IGNORECASE)
            line = compiled.sub(f"<OBJECT {num_objects}>", line)
            num_objects += 1
    return line

class Gary(Chatbot):
    response = "I am Gary"

    def __init__(self):
        super().__init__()
        self.generator = pipeline('text-generation', model='Dizzykong/gpt2-quests-100', tokenizer='gpt2')


    def send_message(self):
        result = self.generator("\n", max_length=200, num_return_sequences=1)[0]
        result = result['generated_text']
        result = result.split('\n')[1]
        result = classifier_templater(result)
        return {"text": result}

    def recv_message(self, message):
        self.response = message
        return super().recv_message(message)