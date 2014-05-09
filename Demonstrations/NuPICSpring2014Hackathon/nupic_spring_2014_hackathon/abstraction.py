import numpy as np
from nupic.research.TP10X2 import TP10X2 as TP
from cept import CeptClient

class CLAModel(object):
    
    def __init__(self):
        self.dim = 64**2
        
        self.tp = TP(numberOfCols=64**2, cellsPerColumn=32,
                    initialPerm=0.5, connectedPerm=0.5,
                    minThreshold=10, newSynapseCount=40,
                    permanenceInc=0.1, permanenceDec=0.00001,
                    activationThreshold=int((64**2 * .02) / 2),
                    globalDecay=0, burnIn=1,
                    checkSynapseConsistency=False,
                    pamLength=10)        

    def train(self, sdr, learning):
        values = self.toArray(sdr, self.dim)
        self.tp.compute(values, learning, computeInfOutput=True)
        predictedCells = self.tp.getPredictedState()
        predictedColumns = predictedCells.max(axis=1)
        predictedBitmap = predictedColumns.nonzero()[0]
        return list(predictedBitmap)
    
    def toArray(self, lst, length):
        res = np.zeros(length, dtype="uint32")
        for val in lst:
            res[val] = 1
        return res


def loadSentences(file):
    with open(file, 'r') as f:
        return [line.strip().split(',') for line in f.readlines()]

def andExpression(term1, term2):
    return '{"and": [{"term": "%s"}, {"term": "%s"}]}' % (term1, term2)


def trainModel(client, model, sentences):
    learning = True
    for i, sentence in enumerate(sentences):
        sdrs = []
        sdrs.append(client.getSDR(sentence[0]))
        sdrs.append(client.getSDR(sentence[1]))
        #sdrs.append(client.getSDR(sentence[2]))
        sdrs.append(client.getSDRexpr(andExpression(sentence[0], sentence[2])))
        for sdr in sdrs:
            predictedBitmap = model.train(sdr, learning)
            
        if (i % 20) == 0:
            print ''
        print '.',
        model.tp.reset()
    print

def queryModel(client, model, queries):
    learning = False
    for query in queries:
        
        for i, term in enumerate(query):
            sdr = client.getSDR(term)
            predictedBitmap = model.train(sdr, learning)
            predictedTerm = client.getSimilarTerms(predictedBitmap, 1)

            if i == len(query)-1:
                print " ".join(query), "=>", ", ".join(predictedTerm)
        model.tp.reset()


if __name__ == '__main__':
    
    client = CeptClient()
    model = CLAModel()
    
    physicists_be = loadSentences('data/physicists_be.txt')
    physicists_like = loadSentences('data/physicists_like.txt')
    politicians_be = loadSentences('data/politicians_be.txt')
    singers_be = loadSentences('data/singers_be.txt')
    singers_like = loadSentences('data/singers_like.txt')
    actors_like = loadSentences('data/actors_like.txt')
    
    queries = loadSentences('data/queries.txt')

    # experiment
    print('Starting training of CLA ...')
    trainModel(client, model, physicists_be)
    trainModel(client, model, singers_be)
    trainModel(client, model, physicists_like)
    trainModel(client, model, singers_like)
    trainModel(client, model, actors_like)
    print('Finished training the CLA.')
    print('Querying the CLA:')
    queryModel(client, model, queries)

