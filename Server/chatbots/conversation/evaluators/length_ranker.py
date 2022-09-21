from chatbots.conversation.evaluators.ranker_base_class import Ranker
# from ranker_base_class import Ranker

class LengthRanker(Ranker):
    def __init__(self):
        pass

    def name(self):
        return "Length Ranker"

    def rank(self, context, sentences):
        scores = [1]*len(sentences)
        for i in range(len(sentences)):
            if len(sentences[i]) > 700:
                scores[i] = 0
            elif len(sentences[i]) > 300:
                scores[i] = .5

        print(self.name() + ": ")
        print(scores)
        return scores

if __name__=="__main__":
    r = LengthRanker()
    context = ['Hello, my name is Nancy.']
    sentences = ['That is a strange thing to say', 'Pleased to meet you!', 'fish are aquasssssssssssssssssssssssddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssstic animals with scales and gills.',"Hi there! I'm Eve.","So what are we supposed to talk about?","Have you seen the movie Iron Man? Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus"]
    r.rank(context, sentences)
