
import nltk

class InputPreProcessor(object):

    def __init__(self):
        pass

    def pre_process(self,text):

        tokens=nltk.word_tokenize(text)
        size=len(tokens)
        tokens_tokens=[]

        for i in range(0,size):
            for j in range(i,size):
                tokens_tokens.append(tokens[i:j+1])
        responses=[]

        for l in tokens_tokens:
            res = " "
            for response in l:
                res=res+" "+response

            responses.append(res)
        return responses









