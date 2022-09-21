from random import sample
from chatbots.Chatbot import Chatbot
from transformers import pipeline
import os
import spacy
from spacy.language import Language
from chatbots.fill_temp import fill_templates
from chatbots.knowledge_graph.query_kg import template_filler
import re

# Adam's Spacy pipeline
@Language.component("templater_component")
def templater_component(doc):
    for token in doc:
      #### Adds an attribute called 'is_template' ####
      get_is_template = lambda token: True if token.ent_type_ in ['PERSON', 'LOC', 'ORG'] else False      
      token.set_extension("is_template", getter=get_is_template, force=True)

      #### Adds an attribute called 'template_text' ####
      get_template_text = lambda token: token.ent_type_ if token.ent_type_ in ['PERSON', 'LOC', 'ORG'] else token.text
      def set_template_text(token, value): 
        token._.template_text = value  
      token.set_extension("template_text", getter=get_template_text, setter=set_template_text, force=True)
        
    return doc

def insert_newlines(text):
    ## Adds newline every 25 characters
    for i in range(0, len(text), 95):
        text = text[:i] + "\n" + text[i:]

    return text

def doc_to_string(doc):
    doc_long = " ".join([token._.template_text for token in doc])
    return insert_newlines(doc_long)

nlp = spacy.load("en_core_web_lg")
nlp.add_pipe("templater_component", name="templater", last=True)



class Kevin(Chatbot):
    def __init__(self):
        #print(os.listdir())
        self.generator = pipeline('text-generation', model='bkwebb23/gpt2-untemplated-quests', tokenizer='gpt2')
        self.response = None

    def fix_templates(self, templated_quest):
        template_vals = ['PERSON', 'ORG', 'LOC', '< class >', '< race >', '< name >']
        replace_vals = ['<person>', '<group>', '<location>', '<person>', '<person>', '<person>']

        for i in range(3):
            if template_vals[i] in templated_quest:
                templated_quest = templated_quest.replace(template_vals[i], replace_vals[i])

        return templated_quest

    def send_message(self):
        print('\nSending message...')

        # Step 1: Extract player message
        # Extract the player's message from the json
        plr_full_msg = self.response['text'].split(":")

        # Check for message from pygame or test client.
        if len(plr_full_msg) == 1:
            plr_full_msg = self.response['text']
        else:
            plr_full_msg = plr_full_msg[1]


        # Cheat and capitalize first letter of player message
        plr_full_msg = plr_full_msg.capitalize()

        # Step 2: Generate response from GPT2
        npc_quest = self.generate(plr_full_msg).rpartition('.')
        
        # Parse everything up to the last period to prevent incomplete sentence
        npc_quest = npc_quest[0] + npc_quest[1]

        # Clean up spaces
        npc_quest = npc_quest.replace('\n', ' ')
        npc_quest = re.sub(' +', ' ', npc_quest)
        print("\nElminate spaces generated text: ", npc_quest)

        # STEP 3: Use Spacy pipeline to create templates
        doc = nlp(npc_quest)
        quest_template = doc_to_string(doc)

        # Clean up spaces in template
        quest_template = quest_template.replace('\n', ' ')
        quest_template = re.sub(' +', ' ', quest_template)

        print("\nTemplated Quest: ", quest_template)

        # Replace template values with ones that work with Abbi's code
        quest_template = self.fix_templates(quest_template)
        
        # Clean up formatting
        quest_template = quest_template.replace('\n', ' ')
        quest_template = re.sub(' +', ' ', quest_template)

        print("\nFixed template: ", quest_template)

        # STEP 4: Fill in templates using knowledge graph
        quest_template = "5->Plr: " + quest_template
        #hard_coded_temp = "Armageddon approaches. Only you can stop it, with the help of <PERSON1>. You must meet them at <LOC1>." 
        #final_quest = fill_templates.fill_in(quest_template)

        template_fill = template_filler()
        final_quest = template_fill.fill_template(quest_template)

        print("\nFinal Quest: ", final_quest)
        
        return {"text": final_quest}

    def recv_message(self, message):
        self.response = message
        return super().recv_message(message)

    def generate(self, input):
        print("Generating message from pipeline...")
        out = self.generator(input, )[0]['generated_text']

        print("\nText output : ", out)
        return out

