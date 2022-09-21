import re
import random
from chatbots.fill_temp.Neo4jDAO import Neo4jDAO

# MINE 
dao = Neo4jDAO(uri="neo4j+s://712b7c09.databases.neo4j.io", user="neo4j", pwd="OBR0Pmixa6JgQ3D70zhmddH7gDzHt2XfoeWRFu5FzoQ")

# FULDA
# dao = Neo4jDAO(uri="neo4j+s://27c53c53.databases.neo4j.io", user="neo4j", pwd="7ir5mGBbgkXvc60tmWLUkwanf6lzj6mQm16YyyUrjOg")

# template = "Armageddon approaches. Only you can stop it, with the help of <person1> and <obj1>. Hurry to <location1>, and make sure <person2> does not find you, or the <group1>."


def query(temp_category):
    # this is a list of all node types in template, in the order given in temp_category, and with duplicates
    # for example: [group obj group location]
    temp_types = [key[0] for key in list(temp_category.keys())]
    assert len(temp_types) == len(temp_category)

    # this is a dictionary that keeps track of duplicates and which indices they have (in temp_category)
    # for example: {"group": [0,2], "obj": [1], "location": [3]}
    mult_dict = dict()
    for key in list(temp_category.keys()):
        if key[0] not in mult_dict:
            mult_dict[key[0]] = [temp_category[key]]
        else:
            mult_dict[key[0]].append(temp_category[key])

    depth = 1
    max_depth = len(temp_types) # this was largely a random choice so that the while loop doesn't go on forever
    res = construct_query(temp_types, mult_dict, depth)
    while res == None and depth <= max_depth:
        res = construct_query(temp_types, mult_dict, depth+1)

    return res


def construct_query(temp_types, mult_dict, depth=1):
    # get a query for a particular center
    for i in range(len(temp_types)):
        query_list = temp_types[i:] + temp_types[0:i]
        assert len(query_list) == len(temp_types)

        # account for change in order from choosing different centers by using modulo
        cypher_query = f"match (x{i}:{temp_types[i]}) " 
        matching = [f"match (x{i})-[*1..{depth}]-(x{j % len(temp_types)}:{temp_types[j % len(temp_types)]}) " for j in range(i+1, i+len(temp_types))]
        for q in matching:
            cypher_query += q

        # account for multiplicity (want different instances of same type to be different nodes)
        is_first = True
        for key in list(mult_dict.keys()):
            mults = mult_dict[key]
            if len(mults) > 1:
                where_statements = [f"where (x{mults[i]}) <> (x{mults[i+1]}) " if (i == 0 and is_first == True) else f"and (x{mults[i]}) <> (x{mults[i+1]}) " for i in range(len(mults)-1)]
                is_first = False
                for w in where_statements:
                    cypher_query += w

        # return in the order we have in the dictionary temp_category, namely 0,1,...,len(temp_category)
        cypher_query += "return x0.name"
        if len(temp_types) > 1: cypher_query += ", "
        print("Template types: ", temp_types)
        print("Length of temp types: ", len(temp_types))
        ret_list = [f"x{i}.name, " for i in range(1,len(temp_types)-1)] # minus one because we don't want trailing comma
        for q in ret_list:
            cypher_query += q
        j = len(temp_types)-1
        if len(temp_types) > 1: cypher_query += f"x{j}.name"
        print("Cypher query: ", cypher_query)

        res = actually_query(cypher_query) 
        if res != None:
            return res
        else: 
            continue

    return None


def actually_query(cypher_query):
    result = dao.query(cypher_query)
    for row in result:
        return [row[i] for i in range(len(row))] # just return first row
    # FIXME does returning the first row give the best fit? (If we need depth 2 to get to a location, but there is a person at depth 1, will first row reflect this closer solution?


def make_dict(temp_words, result):
    assert (len(result)) == (len(temp_words))
    for i in range(len(result)): # this is just to make the filled in quests from my knowledge graph sound better (FIXME)
        if result[i] in ["Angel", "Demon", "Witch"]:
            if result[i] == "Angel":
                result[i] = "Angels"
            elif result[i] == "Demon":
                result[i] = "Demons"
            elif result[i] == "Witch":
                result[i] = "Witches"
            else:
                assert (False)
    return {f"{i}" : result[i] for i in range(len(result))}


def strip_template(template, translate_to_kg):
    new_str = ""
    temp_words = dict()
    for word in template.split():
        if word[0] != '<': # not a template word
            new_str = new_str + word + " "
        else:
            new_word = ""
            mult = -1
            for i in range(len(word)):
                if word[i].isalpha(): new_word += word[i]
                elif word[i].isnumeric(): mult = int(word[i])
                elif word[i] == '>': # if we hit this, there's at most punctuation left
                    punct = word[i+1:] + " "
                    break

            if new_word in translate_to_kg:
                new_word = translate_to_kg[new_word]

            assert mult != -1 # all template words must have a multiplicity
            if (new_word, mult) in temp_words: # accounting for multiplicity
                new_str = new_str + f"{temp_words[(new_word, mult)]}" + punct
            else:
                new_str = new_str + f"{len(temp_words)}" + punct
                temp_words[(new_word, mult)] = f"{len(temp_words)}"
    return new_str, temp_words


def fill_in(template):
    # make templates and knowledge graph compatible (dictionary hard-coded) {words_in_template: corres_word_in_knowledge_graph}
    # translate_to_kg = {"group": "occupation", "object": "obj"} # for my knowledge group and hard-coded templates
    translate_to_kg = {"ORG": "occupation", "PERSON": "person", "LOC": "location"} # for my knowledge group
    # translate_to_kg = {"group": "Group", "obj": "Object", "object": "Object", "location": "Location", "person": "Person"} # for class k.g.

    # set up string
    new_str, temp_words = strip_template(template, translate_to_kg)
    print("Dictionary of templates: ", temp_words)
    print("String to fill in: ", new_str)
    # format of temp_words : temp_words[(word, mult)] = num representing this word in new_str

    # check that all node types in temp_words are actual labels in the knowledge graph
    pos_words = [w[0][0] for w in dao.query("match(n) return labels(n)")]
    for word, mult in temp_words:

        if word not in pos_words:
            print(word)
            raise Exception("Template type is not in knowledge graph.")

    # construct cypher query
    if temp_words == dict(): # no template tokens in quest
        return template
    q = query(temp_words)

    # make dict from output of knowledge graph
    assert (q != None)
    fill_in_dict = make_dict(temp_words, q)
    print("Filled in dictionary for temp: ", fill_in_dict)

    # fill in template
    return new_str.translate(str.maketrans(fill_in_dict))


# print(fill_in(template))

