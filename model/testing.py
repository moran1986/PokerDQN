# -*- coding: utf-8 -*-
import Game, Network, encoder, training
from keras.models import model_from_json

def testAlgo(init=0):
    i = 0
    game = Game.Game(0)

    modelfile = open('model.json')
    model = model_from_json(modelfile.read())
    modelfile.close()
    model.load_weights('model.h5')

    trainSettings = {'epochs': 5,
                     'gamma': 0.975,
                     'epsilon': 0,
                     'batchSize': 40,
                     'buffer': 80,
                     'replay':[],
                     'h':0,
                     'model': model}

    game.startRound()
    while(game.gameNum < 2):
        state = encoder.encodeGame(game)
        game.printGame()
        qVal, betSize = training.predictQ(trainSettings['model'], state, 0)
        game.doBet(qVal, betSize)
        if game.roundFinished:
            game.printGame()
            if len(game.players)==1:
                game=Game.Game(game.gameNum+1)
            game.startRound()
        i += 1 #If we're taking more than 10 actions, just stop, we probably can't win this game
        if (i > 10000):
            print("Game lost; too many moves.")
            break


testAlgo()