import random
import numpy as np

import chatbots.conversation.generators.response_generators as generators
import chatbots.conversation.evaluators.response_evaluators as evaluators
import chatbots.conversation.nlp_pipeline.pipeline as pipeline

class conversation_engine:

    def __init__(self, nlp=None, selected_generators=None, selected_evaluators=None, selected_filters=None, verbose=False):
        self.response_generators = selected_generators if selected_generators else generators.response_generators
        self.evaluators = selected_evaluators if selected_evaluators else evaluators.response_evaluators
        self.filters = selected_filters if selected_filters else evaluators.response_filters
        self.pipeline = nlp if nlp else pipeline.nlp_modules
        print("Active Generators:", [g.name() for g in self.response_generators])
        print("Active Rankers:", [e.name() for e in self.evaluators])
        self.context = {}
        self.context['history'] = []

    def start(self):
        response = generators.greeter.response()['response']
        self.context['previous_response'] = response
        return response

    def start_history(self):
        response = "What would you like to know?"
        self.context['previous_response'] = response
        return response

    def run_nlp_pipeline(self, text):
        for module in self.pipeline:
            result = module.process(text, self.context)
            for key in result:
                self.context[key] = result[key]
            print(module.name(), result)
        print()

    def update_context(self,text):
        self.context['text'] = text
        self.context['history'].append(text)
        self.context['topic'] = ''
        self.run_nlp_pipeline(text)

        # DEPRECATED: these context tags are needed by legacy repsonse generators
        self.context['handpicked_keywords'] = [random.choice(text.split())]
        self.context['strict_topic'] = ''
        self.context['ner'] = {}
        self.context['key_phrases'] = [random.choice(text.split())]

        print("Updated context: ", self.context)

    def argmax_or_rand(self, arr):
        candidates = [0]
        max = arr[0]

        for i, val in enumerate(arr):
            if i == 0:
                continue
            if arr[i] > max:
                candidates = [i]
                max = arr[i]
            elif arr[i] == max:
                candidates.append(i)

        return random.choice(candidates)

    def choose_response(self, responses):
        scores = np.ones(len(responses))
        for evaluator in self.evaluators:
            scores += evaluator.rank(self.context, responses)
        for filter in self.filters:
            scores *= filter.rank(self.context, responses)

        print("Total scores: ")
        print(scores)
        print('\n')
        return responses[self.argmax_or_rand(scores)]

    def chat(self, text, verbose):
        self.update_context(text)
        #responses = ["I'm not sure what to say."]
        responses = []
        sources = []
        for g in self.response_generators:
            g.input_data = self.context
            g.context = self.context
            response = g.response(text)['response']
            #print(g.name())
            #print(response)
            if verbose:
                print('   '+g.name()+": ",response)
            if response:
                if isinstance(response, str):
                    #generator returned a single response
                    responses.append(response)
                    sources.append(g.name())
                else:
                    #generator returned a list of possible responses
                    responses += response
                    sources += [g.name]*len(response)
        response = self.choose_response(responses)
        self.context['previous_response'] = response
        return response
