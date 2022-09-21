# Created by Alex Pixton on 4/13/2022

from chatbots.conversation.generators.response_generator_base_class import ResponseGenerator
from chatbots.conversation.knowledge.Neo4jDAO import Neo4jDAO
from chatbots.conversation.nlp_pipeline.pipeline import spacy
import requests as req
import random
import re

acceptable_short_actions = ["laughs", "smiles", "yells", "pauses", "waits", "shouting", "sighs", "sniffing"]
acceptable_short_responses = ["no", "yes", "ok", "why", "what"]


class TrevorResponseGenerator(ResponseGenerator):
    def __init__(self, verbose=False):
        uri = "neo4j+s://1ca9eb90.databases.neo4j.io"
        user = "neo4j"
        pwd = "gIWKGZDgAKfDs6nGBEpfsoJ67oEeRN9WRfBHi8jbxm4"
        self.ai21_api = "tQoKhPM0AZgWI8O33hd3ZCaBfK9kiTLQ"
        self.verbose = verbose
        try:
            self.kg = Neo4jDAO(uri=uri, user=user, pwd=pwd)
        except:
            print("Error connecting to knowledge graph")

        super(TrevorResponseGenerator, self).__init__()

    def name(self):
        return "Trevor"

    def response(self, input) -> str:
        possible = self._response(input, num=1)
        scored = {}
        for response in possible:
            scored[response] = self._prelim_evaluate(response, input)

        assert scored.items(), "No possible responses"
        return sorted(scored.items(), key=lambda x: x[1], reverse=True)[0][0]

    def _response(self, text, num=5) -> list:
        names = self._find_names(text)

        # get the relevant facts and join into string with parentheses around each fact
        relevant = ')\n('.join(self.get_relevant_facts(text))
        relevant = '(' + relevant + ')'
        query = f'{relevant}\n{random.choice(names) if names else "player"}: "{text}"\nDon Quixote: '
        if self.verbose:
            print(f"facts->{relevant}")
            print(f"query->{query}")
        response = req.post(
            "https://api.ai21.com/studio/v1/j1-jumbo/complete",
            headers={"Authorization": f"Bearer {self.ai21_api}"},
            json={
                "prompt": query,
                "numResults": min(16, num),  # 16 is the max
                "maxTokens": 32,
                "stopSequences": ["."],
                "topKReturn": 0,
                "temperature": 0.7,
                "countPenalty": {"scale": 12.4, "applyToWhiteSpaces": False, "applyToPunctuations": False, "applyToNumbers": False, "applyToStopwords": False, "applyToEmojis": False},
                "frequencyPenalty": {"scale": 12.4, "applyToWhiteSpaces": False, "applyToPunctuations": False, "applyToNumbers": False, "applyToStopwords": False, "applyToEmojis": False},
            }
        ).json()
        assert "completions" in response.keys(), "AI21 not connected"

        # get the text from the api returned completions
        responses = [r["data"]["text"] for r in response['completions']]
        return self._clean_responses(responses)

    def _prelim_evaluate(self, response, input):
        length_score = len(response) / 256
        similar_score = spacy.nlp(response).similarity(spacy.nlp(input))
        return length_score * 0.5 + similar_score


    def _clean_responses(self, responses):
        clean = []
        for response in responses:

            # if it generates text for other characters only keep the first bit
            # ex:   "John: I am doing well. Bill: that's good."  ->  "I am doing well."
            if ':' in response:
                response = response.split(':')[0]
                response = ''.join(response.split('\n')[:-1])
            response = re.sub("Sancho", "player", response)

            # extract any actions from the response and save them separately
            actions = re.findall("[(][A-z0-9\s]+[)]", response)
            actions = [a for a in actions if " " in a or a in acceptable_short_actions]

            # reply without actions must meet minimum length or be in approved list
            reply = re.sub("[(][A-z\s]+[)]", " ", response)
            if (len(reply) < 5 or " " not in reply) and re.match("\w+", reply) not in acceptable_short_responses:
                reply = ""
            reply = re.sub("^\W+", " ", reply)             # remove non-letter characters at start of string
            reply = re.sub("[^A-z0-9!.,'?]+", " ", reply)  # remove unapproved tokens
            reply = re.sub("\n+", " ", reply)              # remove newlines
            reply = re.sub("\s+", " ", reply)              # remove extra spaces

            # add the two pieces together
            if not reply.isalpha():
                response = ' '.join(actions) + reply

            clean.append(response)

        # filter out empty strings and return clean list
        clean = list(filter(bool, clean))
        return clean

    def _find_names(self, doc):
        if type(doc) == str:
            doc = spacy.nlp(doc)
        people = [ent for ent in doc.ents if ent.label_ == "PERSON"]
        if not people:
            people = [tok for tok in doc if tok.pos_ == "PROPN"]
        return people

    def add_knowledge(self, nodes: list = None, relations: list = None):
        """
        :param nodes:
        list of node objects
        node:      tuple(<str>, <dict>)
        :param relations:
        list of relation objects
        relation:  tuple(<node>, <node>, <str>)
        """
        for objType, dictArgs in nodes:
            self.kg.createNode(objType=objType, dictArgs=dictArgs)
        for obj1, obj2, rel in relations:
            self.kg.createEdge(objTypeN1=obj1[0], argsN1=obj1[1],
                               objTypeN2=obj2[0], argsN2=obj2[1],
                               relType=rel)

    def get_relevant_facts(self, text: str):
        # TODO: improve fact finding, maybe only find facts related to single node
        facts = []
        for word in re.sub("\W+", " ", text).split():
            doc = spacy.nlp(word)
            for node in self.kg.getNode("Items", {}):
                quantity, name = [i[1] for i in node.getProps()]
                sim = doc.similarity(spacy.nlp(node.getProps()[1][1]))
                if sim > 0.5:
                    rels = self.kg.getConnectionsWithRel("Items", {"name": name, "quantity": quantity})
                    facts.extend([self._fact_to_sentence(r) for r in rels])

        return facts

    def _fact_to_sentence(self, rel):
        # TODO: actually implement
        s = ""
        if rel.getNode2().getType() == "Items":
            s += rel.getNode2().getProps()[1][1] + " "
        else:
            s += rel.getNode2().getProps()[0][1] + " "
        s += rel.getRel() + " "
        if rel.getNode1().getType() == "Items":
            s += rel.getNode1().getProps()[0][1]
        else:
            s += rel.getNode1().getProps()[1][1]
        return re.sub("_", " ", s)

