from Neo4jDAO import Neo4jDAO


if __name__ == "__main__":
    dao = Neo4jDAO(uri="neo4j+s://1ca9eb90.databases.neo4j.io:7687", user="neo4j", pwd="gIWKGZDgAKfDs6nGBEpfsoJ67oEeRN9WRfBHi8jbxm4")


    # Create KG for backfilling templates

    dao.createNode("Person", {"name": "Trevor"})
    dao.createNode("Person", {"name": "Kevin"})
    dao.createNode("Job", {"name": "Carpenter"})
    dao.createNode("Job", {"name": "Blacksmith"})
    dao.createNode("Location", {"name": "Trevor's House"})
    dao.createNode("Location", {"name": "Kevin's House"})
    dao.createNode("Location", {"name": "Dark Woods"})
    dao.createNode("Location", {"name": "Village Windmill"})
    dao.createNode("Location", {"name": "The Well"})
    dao.createNode("Location", {"name": "Trevor's House"})
    dao.createNode("Group", {"name": "Village Council"})
    dao.createNode("Group", {"name": "Blacksmith Guild"})
    dao.createNode("Object", {"name": "Gold"})
    dao.createNode("Object", {"name": "Armor"})
    dao.createNode("Object", {"name": "Water"})
    dao.createNode("Object", {"name": "Gemstone"})
    dao.createNode("Object", {"name": "Dragon"})
    dao.createNode("Object", {"name": "Giant Spider"})

    dao.createEdge("Person", {"name": "Kevin"}, "Job", {"name": "Carpenter"}, "works_as")
    dao.createEdge("Person", {"name": "Kevin"}, "Group", {"name": "Village Council"}, "member_of")
    dao.createEdge("Person", {"name": "Kevin"}, "Location", {"name": "Kevin's House"}, "lives_in")
    dao.createEdge("Person", {"name": "Kevin"}, "Location", {"name": "Dark Woods"}, "visits")
    dao.createEdge("Person", {"name": "Kevin"}, "Location", {"name": "The Well"}, "visits")
    dao.createEdge("Person", {"name": "Kevin"}, "Object", {"name": "Gold"}, "wants")
    dao.createEdge("Person", {"name": "Kevin"}, "Object", {"name": "Water"}, "needs")
    dao.createEdge("Person", {"name": "Kevin"}, "Object", {"name": "Giant Spider"}, "needs_killed")
    dao.createEdge("Person", {"name": "Trevor"}, "Job", {"name": "Blacksmith"}, "works_as")
    dao.createEdge("Person", {"name": "Trevor"}, "Group", {"name": "Blacksmith Guild"}, "member_of")
    dao.createEdge("Person", {"name": "Trevor"}, "Location", {"name": "Trevor's House"}, "lives_in")
    dao.createEdge("Person", {"name": "Trevor"}, "Location", {"name": "Village Windmill"}, "visits")
    dao.createEdge("Person", {"name": "Trevor"}, "Location", {"name": "The Well"}, "visits")
    dao.createEdge("Person", {"name": "Trevor"}, "Object", {"name": "Armor"}, "makes")
    dao.createEdge("Person", {"name": "Trevor"}, "Object", {"name": "Gold"}, "wants")
    dao.createEdge("Person", {"name": "Trevor"}, "Object", {"name": "Gemstone"}, "wants")
    dao.createEdge("Person", {"name": "Trevor"}, "Object", {"name": "Water"}, "needs")
    dao.createEdge("Person", {"name": "Trevor"}, "Object", {"name": "Dragon"}, "needs_killed")

    dao.close()