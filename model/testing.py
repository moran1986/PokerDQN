# -*- coding: utf-8 -*-
import Game, Network, encoder

def testAlgo(init=0):
    i = 0
    game = Game.Game()
    model = Network.createModel()
    game.startRound()
    status = 1
    #while game still in progress
    while(status == 1):
        betSize = model.predict(encoder.encodeGame(game), batch_size=1)
        game.doBet(betSize)
        if game.roundFinished:
            game.startRound()
        i += 1 #If we're taking more than 10 actions, just stop, we probably can't win this game
        if (i > 10000):
            print("Game lost; too many moves.")
            break


testAlgo()