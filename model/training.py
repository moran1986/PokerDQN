# -*- coding: utf-8 -*-
import Game, Network, encoder, random
import numpy as np
import sys



def train():
    sys.stdout.write("Start training")
    game = Game.Game(0)
    game.startRound()

    trainSettings = {'epochs': 1000,
                     'gamma': 0.975,
                     'epsilon': 0.5,
                     'batchSize': 4,
                     'buffer': 8,
                     'replay':[],
                     'h':0,
                     'model': Network.createModel()}
    experienceCache = [None] * len(game.players)
    while game.gameNum < trainSettings['epochs']:
        playerId = game.turn
        state = encoder.encodeGame(game)
        qVal, betSize = predictQ(trainSettings['model'], state, trainSettings['epsilon'])
        game.doBet(qVal, betSize)
        game.printGame()

        if game.gameNum%100 == 0 and game.gameNum>0:
            textfile = open("model.json", 'w')
            textfile.write(trainSettings['model'].to_json())
            textfile.close()
            trainSettings['model'].save_weights('model.h5', overwrite=True)

        if experienceCache[playerId] is not None:
            (oldState, oldBetSize) = experienceCache[playerId]
            totalExperience = (oldState, oldBetSize, 0, state, False)
            doTrain(trainSettings, totalExperience)
            experienceCache[playerId] = (state, betSize)
        else:
            experienceCache[playerId] = (state, betSize)

        if game.roundFinished:
            for i in range(len(game.players)):
                if experienceCache[i] is not None:
                    (oldState, oldBetSize) = experienceCache[i]
                    game.turn = i
                    newState = encoder.encodeGame(game)
                    totalExperience = (oldState, oldBetSize, game.players[i].reward, newState, True)
                    doTrain(trainSettings, totalExperience)
            if len(game.players)==1:
                game=Game.Game(game.gameNum+1)
            game.startRound()
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
            trainSettings['h'] = 0
        trainSettings['replay'][trainSettings['h']] = experience
        #randomly sample our experience replay memory
        minibatch = random.sample(trainSettings['replay'], trainSettings['batchSize'])
        X_train = []
        y_train = []
        for memory in minibatch:
            #Get max_Q(S',a)
            old_state, betSize, reward, new_state, terminal = memory
            if not terminal:
                newQ, betSize = predictQ(trainSettings['model'], new_state, 0)
                update = (reward + (trainSettings['gamma'] * newQ))
            else:
                update = reward
            y = update
            X_train.append(old_state[0])
            y_train.append(y)

        X_train = np.array(X_train)
        y_train = np.array(y_train)
        trainSettings['model'].train_on_batch(X_train, y_train)


def predictQ(model, state, epsilon):
    state[0,encoder.SIZE-1] = 0
    qvalFold = model.predict(state, batch_size=1)[0,0]
    minimumBet = int(encoder.getCurrentPlayerPotBet(state))
    playerMoney = int(encoder.getCurrentPlayerMoney(state))
    if minimumBet >= playerMoney:
        state[0,encoder.SIZE-1] = playerMoney
        qvalAllIn = model.predict(state, batch_size=1)[0,0]
        if random.random() < epsilon:
            #random action
            if random.random() < 0.5:
                return (qvalAllIn, playerMoney)
            else:
                return (qvalFold, 0)
        #best by Q
        if qvalAllIn > qvalFold:
            return (qvalAllIn, playerMoney)
        else:
            return (qvalFold, 0)
    else:
        if random.random() < epsilon:
            #random action
            randomBet = random.randint(0,playerMoney - minimumBet + 1)
            if randomBet == 0:
                return (qvalFold, 0)
            else:
                bet = randomBet + minimumBet - 1
                state[0,encoder.SIZE-1]=bet
                Q = model.predict(state, batch_size=1)[0,0]
                return (Q, bet)
        #best by Q
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

train()