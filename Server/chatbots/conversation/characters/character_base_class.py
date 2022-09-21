from byu_eve.knowledge.Neo4jDAO import Neo4jDAO
from byu_eve.nlp_pipeline.pipeline import spacy
import re


# some comment

class Character:
    kg = None
    def __init__(self, name: str, uri, user, pwd):
        self.name = name
        try:
            self.kg = Neo4jDAO(uri=uri, user=user, pwd=pwd)
        except:
            print("Error connecting to knowledge graph")

    def __del__(self):
        try:
            self.kg.close()
        except:
            print("Error closing")

    def __str__(self):
        return f"<{self.name}>"

    def response(self, text) -> list:
        """
        Implementation of the response generator
        Do crazy stuff

        :return:
        list of strings of possible answers
        """

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
                    facts.extend([self.fact_to_sentence(r) for r in rels])

        return facts

    def fact_to_sentence(self, rel):
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