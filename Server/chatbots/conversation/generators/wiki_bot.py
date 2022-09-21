# Elizabeth Vargas

import random
from chatbots.conversation.generators.response_generator_base_class import ResponseGenerator
import wikipedia

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')

class WikiResponseGenerator(ResponseGenerator):

    def name(self):
        return "WikiBot"

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def response(self, user):
        # remove stopwords
        words = word_tokenize(user.lower())
        filtered_sent = [w for w in words if not w in self.stop_words]

        # search wikipedia and return the first sentence of the summary
        if len(filtered_sent) >= 1:
            try:
                # get wiki summary
                wiki = wikipedia.summary(' '.join(filtered_sent))

            except:
                # get this response rejected by the evaluator
                return {'response': ' '}

            else:
                # get first sentence
                punctuation = False
                for i in range(len(wiki)):
                    for punct in "!.?":
                        if wiki[i] == punct:
                            wiki = wiki[:i+1]
                            punctuation = True
                            break
                    if punctuation:
                        break

                return {'response': wiki}


        else:
            # get this response rejected by the evaluator
            return {'response': ' '}
