import re
import random
from chatbots.knowledge_graph.Neo4jDAO import Neo4jDAO


class template_filler():

    def __init__(self):
        self.tags_by_string = []

    def get_tags_from_template(self, template_str):
        self.tags_by_string = set([m.group(0) for m in re.finditer('<[^<>]+>', template_str)])

    def parse_query_result(self, res):
        all_vals = []

        for record in res:
            val = record.get('x')
            all_vals.append(val.get('name'))

        
        print("All Vals: ", all_vals)

        return random.choice(all_vals)

    def get_replace_vals(self):
        # Array to add replacment values
        replace = [None for tag in self.tags_by_string]

        # Open dao connection
        dao = Neo4jDAO(uri="neo4j+s://1ca9eb90.databases.neo4j.io:7687", user="neo4j", pwd="gIWKGZDgAKfDs6nGBEpfsoJ67oEeRN9WRfBHi8jbxm4")

        # Loop through each tag in set
        for i, tag in enumerate(self.tags_by_string):
            # Capitalize and extract tag name to query
            curr_tag = tag[1:-1].capitalize()

            print("Current Tag: ", curr_tag)

            # TODO: Likley need to convert adam's tags to readable string for my queries

            # Create Query string
            q_string = f"MATCH (x:{curr_tag}) RETURN x"

            print("Query: ", q_string)
            
            # Query neo4j and get results for all nodes with that tag
            res = dao.query(q_string)
            
            # Parse query results and get back the value to replace
            replacement_val = self.parse_query_result(res)

            # Add to value to replace
            replace[i] = replacement_val

        # Close dao connection
        dao.close()

        # Return list of new values
        return replace

    def fill_template_string(self, original_template, replace_vals):
        for i, tag_to_replace in enumerate(self.tags_by_string):
            new_val = replace_vals[i]

            original_template = original_template.replace(tag_to_replace, new_val)

        return original_template

    def fill_template(self, template_string):
        # Get template tags from template
        self.get_tags_from_template(template_string)

        # Query database for each template
        replacement_values = self.get_replace_vals()

        # Fill values into string
        filled_template = self.fill_template_string(template_string, replacement_values)

        # Return filled template
        return filled_template