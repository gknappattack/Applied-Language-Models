import chatbots.conversation.generators.generator_utils


class ResponseGenerator:

    def __init__(self):
        pass

    def response(self, text):
        # each response generator returns a dict containing not only the text response,
        # but also meta-information such as other information that wants to be conveyed
        return { "response": "base class response" }

    def name(self):
        return str(type(self))
