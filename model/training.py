# -*- coding: utf-8 -*-
import Game, Network, encoder, random
import numpy as np
import sys
from keras.models import model_from_json



def train():
    sys.stdout.write("Start training")
    game = Game.Game(0)
    game.startRound()

    #modelfile = open('model.json')
    #model = model_from_json(modelfile.read())
    #modelfile.close()
    #model.load_weights('model.h5')

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
        (cards, state) = encoder.encodeGame(game)

        (qVal, betSize, randomQ) = predictQ(trainSettings['model'], cards, state, trainSettings['epsilon'])
        game.doBet(qVal, betSize, randomQ)
        game.printGame()
        experienceCache[playerId] = (cards, state, betSize)

        if game.gameNum%100 == 0 and game.gameNum>0:
            textfile = open("model.json", 'w')
            textfile.write(trainSettings['model'].to_json())
            textfile.close()
            trainSettings['model'].save_weights('model.h5', overwrite=True)




        if game.roundFinished:
            for i in range(len(game.players)):
                if experienceCache[i] is not None:
                    (oldCards, oldState, oldBetSize) = experienceCache[i]
                    game.turn = i
                    (newCards, newState) = encoder.encodeGame(game)
                    totalExperience = (oldCards, oldState, oldBetSize, game.players[i].reward, newCards, newState, True)
                    doTrain(trainSettings, totalExperience)

            if len(game.players)==1:
                game=Game.Game(game.gameNum+1)
            game.startRound()
            if trainSettings['epsilon'] > 0.1: #decrement epsilon over time
                trainSettings['epsilon'] -= (1/trainSettings['epochs'])
        else:
            gameCopy = game.copy()
            ((newCards, newState), reward, terminal) = getNewState(gameCopy, trainSettings['model'], playerId)
            totalExperience = (cards, state, betSize, reward, newCards, newState, terminal)
            doTrain(trainSettings, totalExperience)

def getNewState(game, model, playerId):
    while True:
        if game.roundFinished:
            game.turn = playerId
            return (encoder.encodeGame(game), game.players[playerId].reward, True)
        elif game.turn==playerId:
            return (encoder.encodeGame(game),0, False)
        (cards, state) = encoder.encodeGame(game)
        (qVal, betSize, randomQ) = predictQ(model, cards, state, 0)
        game.doBet(qVal, betSize, randomQ)


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
        cards_train = []
        states_train = []
        bets_train = []
        y_train = []
        for memory in minibatch:
            #Get max_Q(S',a)
            old_cards, old_state, betSize, reward, new_cards, new_state, terminal = memory
            if not terminal:
                (newQ, newBetSize, randomQ) = predictQ(trainSettings['model'], new_cards, new_state, 0)
                update = (reward + (trainSettings['gamma'] * newQ))
            else:
                update = reward
            y = update
            cards_train.append(old_cards[0])
            states_train.append(old_state[0])
            bets_train.append(betSize)
            y_train.append(y)

        cards_train = np.array(cards_train)
        states_train = np.array(states_train)
        bets_train = np.array(bets_train)
        y_train = np.array(y_train)

        bets_train = bets_train.reshape((4,1))
        y_train = y_train.reshape((4,1))
        trainSettings['model'].train_on_batch(data={'cards': cards_train, 'state':states_train, 'bet':bets_train, 'output':y_train})


def predictQ(model, cards, state, epsilon):
    bet = np.zeros((1,1))
    qvalFold = model.predict(data={'cards':cards, 'state':state, 'bet': bet}, batch_size=1)['output'][0,0]
    minimumBet = int(encoder.getCurrentPlayerPotBet(state))
    playerMoney = int(encoder.getCurrentPlayerMoney(state))
    if minimumBet >= playerMoney:
        bet[0,0]=playerMoney
        qvalAllIn = model.predict(data={'cards':cards, 'state':state, 'bet': bet}, batch_size=1)['output'][0,0]
        if random.random() < epsilon:
            #random action
            if random.random() < 0.5:
                return (qvalAllIn, playerMoney, True)
            else:
                return (qvalFold, 0, True)
        #best by Q
        if qvalAllIn > qvalFold:
            return (qvalAllIn, playerMoney, False)
        else:
            return (qvalFold, 0, False)
    else:
        if random.random() < epsilon:
            #random action
            randomBet = random.randint(0,playerMoney - minimumBet + 1)
            if randomBet == 0:
                return (qvalFold, 0, True)
            else:
                bet[0,0] = randomBet + minimumBet - 1
                Q = model.predict(data={'cards':cards, 'state':state, 'bet': bet}, batch_size=1)['output'][0,0]
                return (Q, bet[0,0], True)
        #best by Q
        (maxQ, bestBet) = findMinimum(model, cards, state, minimumBet, playerMoney)
        if maxQ > qvalFold:
            return (maxQ, bestBet, False)
        else:
            return (qvalFold, 0, False)


def findMinimum(model, cards, state, start, end):
    bet = np.zeros((1,1))
    bet[0,0]=end
    maxQ = model.predict(data={'cards':cards, 'state':state, 'bet': bet}, batch_size=1)['output'][0,0]
    bestBet = end
    for i in range(start,end):
        bet[0,0]=i
        qVal = model.predict(data={'cards':cards, 'state':state, 'bet': bet}, batch_size=1)['output'][0,0]
        if qVal > maxQ:
            maxQ=qVal
            bestBet = i
    return (maxQ, bestBet)

train()