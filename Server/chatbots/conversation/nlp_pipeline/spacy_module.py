
from chatbots.conversation.nlp_pipeline.nlp_base_class import pipeline_module

class SpacyNLP(pipeline_module):

    def __init__(self):
        import spacy
        self.nlp = spacy.load("en_core_web_lg")

    def name(self):
        return "spacy NLP"

    def process(self, text, context=None):
        test = self.nlp("test")
        doc = self.nlp(text)
        return_dict = {}
        return_dict['lemma'] = [word.lemma_ for word in doc]
        return_dict['pos'] = [word.tag_ for word in doc]
        return_dict['dependencies'] = [word.dep_ for word in doc]
        return_dict['keywords'] = [word.text for word in doc if not word.is_stop]
        return_dict['named_entities'] = [ent.text for ent in doc.ents]
        return return_dict
