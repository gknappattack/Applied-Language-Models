from byu_eve.characters.character_base_class import Character, spacy
import requests as req
import random
import re

acceptable_short_actions = ["laughs", "smiles", "yells", "pauses", "waits", "shouting", "sighs", "sniffing"]
acceptable_short_responses = ["no", "yes", "ok", "why", "what"]


class DonQuarlos(Character):
    def __init__(self, verbose=False):
        uri = "neo4j+s://c36caefa.databases.neo4j.io"
        user = "neo4j"
        pwd = "CLCEK1Bu6NFpq81vJQEb6ZPiyBLxpnnUv4t4gtPHy8A"
        self.ai21_api = "tQoKhPM0AZgWI8O33hd3ZCaBfK9kiTLQ"
        self.verbose = verbose

        super(DonQuarlos, self).__init__("Don Quarlos", uri, user, pwd)

    def response(self, input) -> list:
        possible = self._response(input, num=30)
        scored = {}
        for response in possible:
            scored[response] = self.evaluate(response, input)

        assert scored.items(), "No possible responses"
        return sorted(scored.items(), key=lambda x: x[1], reverse=True)

    def _response(self, text, num=10) -> list:
        names = self.__find_names(text)

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
                "maxTokens": 64,
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
        return self.clean_responses(responses)

    def evaluate(self, response, input):
        length_score = len(response) / 256
        similar_score = spacy.nlp(response).similarity(spacy.nlp(input))
        return length_score + similar_score


    def clean_responses(self, responses):
        clean = []
        for response in responses:

            # if it generates text for other characters only keep the first bit
            # ex:   "John: I am doing well. Bill: that's good."  ->  "I am doing well."
            if ':' in response:
                response = response.split(':')[0]
                response = ''.join(response.split('\n')[:-1])
            response = re.sub("Sancho", "player", response)

            # extract any actions from the response and save them seperate
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

    def __find_names(self, doc):
        if type(doc) == str:
            doc = spacy.nlp(doc)
        people = [ent for ent in doc.ents if ent.label_ == "PERSON"]
        if not people:
            people = [tok for tok in doc if tok.pos_ == "PROPN"]
        return people
