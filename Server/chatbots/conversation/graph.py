import spacy
from spacy.lang.en import English
import networkx as nx
import matplotlib.pyplot as plt

# Will Wardinsky

class KnowledgeGraph:

    def __init__(self):
        pass

    def getSentences(self, text):
        nlp = English()
        nlp.add_pipe('sentencizer')
        document = nlp(text)
        return [sent.text.strip() for sent in document.sents]

    def printToken(self, token):
        print(token.text, "->", token.dep_)

    def appendChunk(self, original, chunk):
        return original + ' ' + chunk

    def isRelationCandidate(self, token):
        deps = ["ROOT", "adj", "attr", "agent", "amod"]
        return any(subs in token.dep_ for subs in deps)

    def isConstructionCandidate(self, token):
        deps = ["compound", "prep", "conj", "mod"]
        return any(subs in token.dep_ for subs in deps)

    def processSubjectObjectPairs(self, tokens):
        subj = ''
        obj = ''
        relation = ''
        build_subj = ''
        build_obj = ''
        for token in tokens:
            # printToken(token)
            if "punct" in token.dep_:
                continue
            if self.isRelationCandidate(token):
                relation = self.appendChunk(relation, token.lemma_)
            if self.isConstructionCandidate(token):
                if build_subj:
                    build_subj = self.appendChunk(build_subj, token.text)
                if build_obj:
                    build_obj = self.appendChunk(build_obj, token.text)
            if "subj" in token.dep_:
                subj = self.appendChunk(subj, token.text)
                subj = self.appendChunk(build_subj, subj)
                build_subj = ''
            if "obj" in token.dep_:
                obj = self.appendChunk(obj, token.text)
                obj = self.appendChunk(build_obj, obj)
                build_obj = ''
        print(subj.strip(), ",", relation.strip(), ",", obj.strip())
        return subj.strip(), relation.strip(), obj.strip()

    def processSentence(self, sentence):
        nlp_model = spacy.load('en_core_web_sm')
        tokens = nlp_model(sentence)
        return self.processSubjectObjectPairs(tokens)

    def printGraph(self, triples):
        kn = nx.Graph()
        for triple in triples:
            kn.add_node(triple[0])
            kn.add_node(triple[1])
            kn.add_node(triple[2])
            kn.add_edge(triple[0], triple[1])
            kn.add_edge(triple[1], triple[2])
        pos = nx.spring_layout(kn)
        plt.figure(figsize=(12, 8))
        nx.draw(kn, pos, edge_color='black', width=1, linewidths=1,
                node_size=500, node_color='skyblue', alpha=0.9,
                labels={node: node for node in kn.nodes()})
        plt.axis('off')
        plt.show(block=False)
        plt.pause(10)
        plt.close()

    def plot(self, text):
        sentences = self.getSentences(text)
        triples = []
        # print(text)
        for sentence in sentences:
            triples.append(self.processSentence(sentence))
        self.printGraph(triples)




