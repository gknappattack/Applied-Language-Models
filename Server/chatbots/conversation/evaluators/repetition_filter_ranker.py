from chatbots.conversation.evaluators.ranker_base_class import Ranker

import re


class RepetitionFilterRanker(Ranker):
    def __init__(self):
        Ranker.__init__(self)

    def name(self):
        return "Repetition Filter Ranker"

    def rank(self, context, sentences):
        scores = [1] * len(sentences)
        for i, sent in enumerate(sentences):
            if "previous_response" in context:
                if sent in context["previous_response"]:
                    scores[i] = 0
        return scores


if __name__ == "__main__":
    r = RepetitionFilterRanker()
    context = {"previous_response": "Hello! How are you?"}
    sentences = ['That is a strange thing to say', 'Pleased to meet you! jerk',
                 'fish are aquatic animals with scales, Butts and gills.', "Hi assimilate there! I'm Eve.",
                 "Hello! How are you?", "Have you seen the movie Iron Man?"]
    scores = r.rank(context, sentences)
    print(scores)

