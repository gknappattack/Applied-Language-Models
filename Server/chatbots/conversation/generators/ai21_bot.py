# Elizabeth Vargas
import torch
import re
import requests
from chatbots.conversation.generators.response_generator_base_class import ResponseGenerator


class AI21ResponseGenerator(ResponseGenerator):

    def name(self):
        return "AI21Bot"

    def __init__(self):
        pass

    def response(self, user):

        # input to model
        model_input = "User: " + user + "\nBot:"

        print("Input to Jurrasic: ", model_input)

        res = requests.post(
          "https://api.ai21.com/studio/v1/j1-large/complete",
          headers={"Authorization": "Bearer 5l7xikNVesvNUmLH1XkjoDxBGzqNtrtp"},
          json={
            "prompt": model_input,
            "numResults": 3,
            "maxTokens": 20,
            "stopSequences": ["."],
            "topKReturn": 0,
            "temperature": 0.4
          }
        )

        # get different responses
        responses = []

        for i in range(3):
            text = res.json()['completions'][i]['data']['text']

            # remove Bot: from response
            if 'Bot:' in text:
                text = text[:re.search('Bot:', text).start()]

            # trim text to newline
            if '\n' in text:
                text = text[:re.search('\n', text).start()]

            responses.append(text)

        return {'response': responses}
