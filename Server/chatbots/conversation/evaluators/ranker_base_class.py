
class Ranker:
    def __init__(self):
        self.preferred_weight = 1.0  #How much credence this ranker thinks the main program should give its scores

    def name(self):
        return type(self)

    def rank(self, context, sentences):
        raise ValueError("Error: Ranker base class rank() function cannot be called directly.")

if __name__=="__main__":
    r = Ranker()

