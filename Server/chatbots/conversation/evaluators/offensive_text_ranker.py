from chatbots.conversation.evaluators.ranker_base_class import Ranker
#from ranker_base_class import Ranker

import re
import string

class OffensiveTextRanker(Ranker):
    def __init__(self):
        pass

    def name(self):
        return "Offensive Text Ranker"

    def rank(self, context, sentences):
        offensive_terms = ["anal","anus","anuses","arse","ass","asses","ballsack","ballsacks","balls","bastard","bastards","bitch","bitches","biatch","blowjob","blowjobs","blow job","bollock","bollok","boner","boob","boobs","bugger","bum","bums","butt","butts","buttplug","clitoris","cock","cocks","coon","crap","cunt","cunts","damn","damnit","dick","dicks","dildo","dildos","dyke","fag","fags","feck","fellate","fellatio","felching","fuck","fucking","fucks","fudgepacker","fudge packer","flange","goddamn","hate","hates","hell","homo","jerk","jerks","jerk off","jizz","kill","kills","knobend","knob end","labia","lmao","lmfao","muff","nigger","niggers","nigga","niggas","omg","penis","penises","piss","pissing","poop","pooping","prick","pricks","pube","pubes","pussy","pussies","queer","scrotum","sex","shit","slut","sluts","smegma","spunk","tit","tits","tosser","turd","turds","twat","vagina","vaginas","wank","wanks","whore","whores","wtf"]
        scores = [1]*len(sentences)
        for i in range(len(sentences)):
            stripped = re.findall(r'\b[a-z]+\b', sentences[i].casefold())
            if any(term in stripped for term in offensive_terms):
                scores[i] = 0
        print(self.name() + ": ")
        # print(sentences)
        print(scores)
        return scores

if __name__=="__main__":
    r = OffensiveTextRanker()
    context = ['Hello, my name is Nancy.']
    sentences = ['That is a strange thing to say', 'Pleased to meet you! jerk', 'fish are aquatic animals with scales, Butts and gills.',"Hi assimilate there! I'm Eve.","So what are we supposed to talk about buttplug?","Have you seen the movie Iron Man?"]
    r.rank(context, sentences)
    
