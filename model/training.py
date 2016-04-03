# -*- coding: utf-8 -*-
import Game, Network, encoder, random
import numpy as np
import sys



def train():
    sys.stdout.write("Start training")
    game = Game.Game()
    game.startRound()
    gameNum = 0

    trainSettings = {'epochs': 3000,
                     'gamma': 0.975,
                     'epsilon': 1,
                     'batchSize': 40,
                     'buffer': 80,
                     'replay':[],
                     'h':0,
                     'model': Network.createModel()}
    experienceCache = [None] * len(game.players)
    while gameNum < trainSettings['epochs']:
        playerId = game.turn
        state = encoder.encodeGame(game)
        qVal, betSize = predictQ(trainSettings['model'], state)
        game.doBet(betSize)
        game.printGame()

        if experienceCache[playerId] is not None:
            (oldState, oldBetSize) = experienceCache[playerId]
            totalExperience = (oldState, oldBetSize, 0, state)
            doTrain(trainSettings, totalExperience)
            experienceCache[playerId] = (state, betSize)
        else:
            experienceCache[playerId] = (state, betSize)

        if game.roundFinished:
            for i in range(len(game.players)):
                if experienceCache[i] is not None:
                    (oldState, oldBetSize) = experienceCache[playerId]
                    game.turn = i
                    newState = encoder.encodeGame(game)
                    totalExperience = (oldState, oldBetSize, game.players[i].reward, newState)
                    doTrain(trainSettings, totalExperience)
            if len(game.players)==1:
                game=Game.Game()
            game.startRound()
            gameNum+=1
            if trainSettings['epsilon'] > 0.1: #decrement epsilon over time
                trainSettings['epsilon'] -= (1/trainSettings['epochs'])
            experienceCache = [None] * len(game.players)




def doTrain(trainSettings, experience):
    #Experience replay storage
    if (len(trainSettings['replay']) < trainSettings['buffer']): #if buffer not filled, add to it
        trainSettings['replay'].append(experience)
    else: #if buffer full, overwrite old values
        if (trainSettings['h'] < (trainSettings['buffer']-1)):
            trainSettings['h'] += 1
        else:
            h = 0
        trainSettings['replay'][trainSettings['h']] = experience
        #randomly sample our experience replay memory
        minibatch = random.sample(trainSettings['replay'], trainSettings['batchSize'])
        X_train = []
        y_train = []
        for memory in minibatch:
            #Get max_Q(S',a)
            old_state, betSize, reward, new_state = memory
            if reward == 0: #non-terminal state
                newQ, betSize = predictQ(trainSettings['model'], new_state)
                update = (reward + (trainSettings['gamma'] * newQ))
            else: #terminal state
                update = reward
            y = update
            X_train.append(old_state[0])
            y_train.append(y)

        X_train = np.array(X_train)
        y_train = np.array(y_train)
        trainSettings['model'].fit(X_train, y_train, batch_size=trainSettings['batchSize'], nb_epoch=1, verbose=1)


def predictQ(model, state):
    state[0,encoder.SIZE-1] = 0
    qvalFold = model.predict(state, batch_size=1)[0,0]
    minimumBet = int(encoder.getCurrentPlayerPotBet(state))
    playerMoney = int(encoder.getCurrentPlayerMoney(state))
    if minimumBet >= playerMoney:
        state[0,encoder.SIZE-1] = playerMoney
        qvalAllIn = model.predict(state, batch_size=1)
        if qvalAllIn > qvalFold:
            return (qvalAllIn, playerMoney)
        else:
            return (qvalFold, 0)
    else:
        (maxQ, bestBet) = findMinimum(model, state, minimumBet, playerMoney)
        if maxQ > qvalFold:
            return (maxQ, bestBet)
        else:
            return (qvalFold, 0)


def findMinimum(model, state, start, end):
    state[0,encoder.SIZE-1]=end
    maxQ = model.predict(state, batch_size=1)[0,0]
    bestBet = end
    for i in range(start,end):
        state[0,encoder.SIZE-1]=i
        qVal = model.predict(state, batch_size=1)[0,0]
        if qVal > maxQ:
            maxQ=qVal
            bestBet = i
    return (maxQ, bestBet)
