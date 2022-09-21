import json
import requests
import sys
import os
from chatbots.conversation.generators.generator_utils import custom_stop_words, break_long_response
from chatbots.conversation.generators.response_generator_base_class import ResponseGenerator
import random

#
# ----------------------
# DuckDuckGoResponseGenerator
# description:  Queries the DuckDuckGo Instant Answer API.
# role:         answer

def remove_doubles(text):
    words = text.split(' ')
    new_words = []
    if len(words) < 2:
         return text
    for i in range(len(words)-1):
        if words[i] != words[i+1]:
            new_words.append(words[i])
    return ' '.join(new_words)

class DuckDuckGoResponseGenerator(ResponseGenerator):
    def name(self):
        return "DuckDuckGo"

    def response(self, text):
        try:
            if text in custom_stop_words:
                return {'response':""}
            #result = duckduckgo.get_zci(text, urls=False).replace("Sorry, no results.", "")
            #result = json.loads(plain_text)

            keywords = self.context['keywords']

            responses = []
            for keyword in keywords:
                url = 'https://api.duckduckgo.com?q="' + keyword + '"&format=json'
                plain_text = requests.get(url).text
                response_object = json.loads(plain_text)
                if response_object['Abstract']:
                    result = response_object['AbstractText']
                elif response_object['RelatedTopics']:
                    result = response_object['RelatedTopics'][0]['Text']
                else:
                    result = ""
                if "http" in result:
                    if "wikipedia" in result:
                        result = get_wikipedia_summary(result.split('/')[-1].replace('_', ' '))
                    else:
                        result = re.sub(r"http\S+", "", result)
                response, more_info = break_long_response(result, word_limit=16, sentence_limit=1)
                if '...' in response:
                    response = result
                if response: responses.append(remove_doubles(response))

            if not responses: responses = ""
            return {
                "response": responses,
                "more_info": more_info,
            }
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print("Exception in DuckDuckGoResponseGenerator. {}".format(e))
            return {'response':""}

