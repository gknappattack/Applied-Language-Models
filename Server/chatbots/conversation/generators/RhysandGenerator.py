# Written by David Weber

import logging
import spacy
import numpy as np
import torch
from transformers import (
	MODEL_WITH_LM_HEAD_MAPPING,
	AutoTokenizer,
)
try:
	from torch.utils.tensorboard import SummaryWriter
except ImportError:
	from tensorboardX import SummaryWriter
from generators.response_generator_base_class import ResponseGenerator

# Configs
logger = logging.getLogger(__name__)

MODEL_CONFIG_CLASSES = list(MODEL_WITH_LM_HEAD_MAPPING.keys())
MODEL_TYPES = tuple(conf.model_type for conf in MODEL_CONFIG_CLASSES)

save_location = "/content/gdrive/MyDrive/Code/SiriClass/FineTuning/model_1"
model = torch.load(save_location)


###############################################################################################
#			NEO4J CONNECTION
#
#	This class simply provides a connection to the Neo4j Database
#
#	To avoid confusion, note that the connection information is provided as arguments to
#	this class.
#
#################################################################################################

from neo4j import GraphDatabase

class Neo4jConnection:
	
	def __init__(self, uri, user, pwd):
		self.__uri = uri
		self.__user = user
		self.__pwd = pwd
		self.__driver = None
		try:
			self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
		except Exception as e:
			print("Failed to create the driver:", e)
	
	def close(self):
		if self.__driver is not None:
			self.__driver.close()
	
	def query(self, query, db=None):
		assert self.__driver is not None, "Driver not initialized!"
		session = None
		response = None
		try:
			session = self.__driver.session(database=db) if db is not None else self.__driver.session()
			response = list(session.run(query))
		except Exception as e:
			print("Query failed:", e)
		finally:
			if session is not None:
				session.close()
		return response


###############################################################################################
#			VERB FILTER
#
#	This class contains code to select verbs from the knowledge graph based on cosine
#	similarity. It does not query the graph. It also contains code for a future feature to
#	filter what info goes into the graph based on verbs that tend to be part of memorable
#	sentences.
#
#################################################################################################

class VerbFilter:
	def __init__(self):
		module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
		self.gmodel = hub.load(module_url)
		print("module %s loaded" % module_url)
		
		self.VERBS = ["possesses", "loves", "related to", "is", "hates", "needs", "profession", "location", "father",
					  "mother", "sister", "brother", "quested", "likes", "married", "age", "kill", "create"]
		self.VERBS_EMB = self.gmodel(self.VERBS)
		self.MIN_SIMILARITY = .5  # NEXT: Needs fine tuning.
	
	def cosine_diff(self, u, v):
		return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
	
	def pick_most_similar_word(self, query_word, existing_words, existing_embeddings, return_query_embedding=False):
		# assert len(existing_embeddings) == len(existing_words)
		query_embedding = self.gmodel([query_word])[0]
		if existing_embeddings == None:
			existing_embeddings = self.gmodel(existing_words)
		
		# Calculate similarities to the VERBS words
		similarities = []
		for i in range(len(existing_embeddings)):
			curr_emb = existing_embeddings[i]
			sim = self.cosine_diff(query_embedding, curr_emb)
			similarities.append(sim)
		
		# Return most similar verb
		most_sim_index = np.argmax(similarities)
		max_sim = similarities[most_sim_index]
		most_sim_word = existing_words[most_sim_index]
		if max_sim < self.MIN_SIMILARITY:
			# Don't return a word if nothing is similar enough.
			if return_query_embedding == True:
				return None, None, query_embedding
			else:
				return None, None
		most_sim_embedding = existing_embeddings[most_sim_index]
		if return_query_embedding == True:
			return most_sim_word, most_sim_embedding, query_embedding
		else:
			return most_sim_word, most_sim_embedding
	
	def get_best_preselected_verb(self, query_verb):
		return self.pick_most_similar_word(query_verb, self.VERBS, self.VERBS_EMB)


##################################################################################################
#			KNOWLEDGE GRAPH GENERATOR
#
#	This class generates responses from the knowledge graph.
#
#	It contains the knowledge graph cypher query along
#	with the code to select and format the tuples.
#
#	USAGE EXAMPLE:
#		kgg = KnowledgeGraphGenerator()
#		response = kgg.respond_to_user("What does Rhysand hate most?")
# 		print(response)
#
###################################################################################################

## TODO: Figure out why "hub" from "transformers" won't load.

# from transformers import hub

class KnowledgeGraphGenerator():
	def __init__(self):
		self.retrieve_graph_tups()
		self.v_filter = VerbFilter()
		self.nlp = spacy.load('en_core_web_sm')
	
	def prep_tup(self, tup):
		verb = tup[1]
		if verb == "has_trait":
			verb = "is"
		elif verb == "posseses":
			verb = "possesses a"
		sent = tup[0] + " " + verb + " " + tup[2] + ". "
		return sent
	
	def retrieve_graph_tups(self):
		neo = Neo4jConnection('neo4j+s://3cbe8913.databases.neo4j.io:7687', 'neo4j',
							  'EdiM93nyFmVIK_w0SssZJX4JMTJtkGwJdqoJSAR5YIY')
		# neo = Neo4jConnection('bolt://localhost:7687', 'neo4j', 'Rhysand')
		res = neo.query("match (n:Person {name: 'Rhysand'})-[r]->(m) return n,r,m")
		print(res)
		
		# Pull tuples out of neo4j response.
		self.tups = []
		self.verb_set = set()
		for r in res:
			tup = ("Rhysand", r[1].type, r[2]._properties["name"])
			self.tups.append(tup)
			self.verb_set.add(r[1].type)
	
	def respond_to_user(self, prompt):
		doc = self.nlp(prompt)
		
		# Get verbs out of prompt
		verbs = set()
		for token in doc:
			if token.pos_ == "VERB":
				verbs.add(token.text)
		
		# Get matching knowledge tuples.
		possible_responses = []
		for v in verbs:
			# NEXT: Change it so that it finds the knowledge graph tuple with the most similar first two words of tuple
			best_verb, _ = self.v_filter.pick_most_similar_word(v, list(self.verb_set), existing_embeddings=None,
																return_query_embedding=False)
			for tup in self.tups:
				if best_verb == tup[1]:
					possible_responses.append(self.prep_tup(tup))
		
		if 0 == len(possible_responses):
			return None
		else:
			return np.random.choice(possible_responses)


###############################################################################################
#			RHYSAND GENERATOR
#
#	This class loads and runs the GPT2 generator. It also has the ability to choose to
#	deliver a response from a knowledge graph generator.
#
#################################################################################################

class RhysandGenerator(ResponseGenerator):
	def __init__(self):
		self.load_model()
		# self.kgg = KnowledgeGraphGenerator()
		self.tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
		self.step = 0
	
	def load_model(self):
		from google.colab import drive
		drive.mount('/content/gdrive')
		save_location = "/content/gdrive/MyDrive/CS/ai_models/DavidsGPT2Model/RebelBot2"
		self.gpt2_model = torch.load(save_location)
	
	def gpt2generate(self):
		new_user_input_ids = self.tokenizer.encode(input(">> User:") + self.tokenizer.eos_token, return_tensors='pt')
		# print(new_user_input_ids)
		# append the new user input tokens to the chat history
		if self.step > 0:
			bot_input_ids = torch.cat([self.chat_history_ids, new_user_input_ids], dim=-1)
		else:
			bot_input_ids = new_user_input_ids
		# generated a response while limiting the total chat history to 1000 tokens,
		self.step = self.step + 1
		self.chat_history_ids = self.gpt2_model.generate(
			bot_input_ids, max_length=200,
			pad_token_id=self.tokenizer.eos_token_id,
			no_repeat_ngram_size=3,
			do_sample=True,
			top_k=100,
			top_p=0.7,
			temperature=0.2
		)
		
		# pretty print last ouput tokens from bot
		# print("RebelBot: {}".format(self.tokenizer.decode(self.chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)))
		
		# pretty print last ouput tokens from bot
		return "RebelBot: {}".format(
			self.tokenizer.decode(self.chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True))
	
	def generate(self, prompt):
		# kgg_str = self.kgg.respond_to_user(prompt)
		# if kgg_str:
		# 	return kgg_str
		# else:
		return self.gpt2generate()
	
	def response(self, text):
		# each response generator returns a dict containing not only the text response,
		# but also meta-information such as other information that wants to be conveyed
		response_str = self.generate(text)
		return { "response": response_str }


###############################################################################################
#			RHYSAND GENERATOR USAGE EXAMPLE.
#
#	To run this in Google Colab, copy this whole file, uncomment this section, and then
#	replace the ResponseGenerator import with the actual contents of the ResponseGenerator
# 	file. You will also need to change where the GPT2 model loads from. Hopefully, it'll work
# 	right away then.
#
# import random
#
# rhysand = RhysandGenerator()
#
# response_generators = [rhysand]
#
# if __name__=="__main__":
#     sample_texts = ["I'm having a bad day", "I feel so sad.", "Tell me about cats", "What is minecraft", "minecraft", "are you a robot", "I just want to die"]
#     response = ""
#     for g in response_generators:
#         print('\n'+g.name())
#         for t in sample_texts:
#             g.input_data = {"previous_response":response,
#                             "handpicked_keywords":[random.choice(t.split())],
#                             "topic":'books',
#                             "strict_topic":'books',
#                             "ner": {},
#                             "key_phrases":[random.choice(t.split())],
#                             "text":t}
#             response = g.response(t)['response']
#             print('   '+response)
#
#################################################################################################