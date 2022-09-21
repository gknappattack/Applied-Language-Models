import random

from chatbots.conversation.evaluators import length_ranker
from chatbots.conversation.evaluators import offensive_text_ranker
from chatbots.conversation.evaluators import keyword_match_ranker
from chatbots.conversation.evaluators import repetition_filter_ranker

length_ranker = length_ranker.LengthRanker()
offensive_text_ranker = offensive_text_ranker.OffensiveTextRanker()
k_m_ranker = keyword_match_ranker.KeywordMatchRanker()
rep_ranker = repetition_filter_ranker.RepetitionFilterRanker()

#evaluating the responses:
response_evaluators = [length_ranker, k_m_ranker]

#filtering the responses
response_filters = [offensive_text_ranker, rep_ranker]
