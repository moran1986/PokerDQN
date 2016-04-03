# -*- coding: utf-8 -*-
import numpy as np

SIZE = 574


def getCurrentPlayerMoney(state):
    return state[0,54]-state[0,53]

def getCurrentPlayerPotBet(state):
    return state[0,520]-state[0,512]

def encodeGame(game):
    encodedPlayers = []
    for i in range(8):
        playerPos =  (i + game.turn)%8
        if playerPos < len(game.players):
            encodedPlayers.append(encodePlayer(game.players[playerPos]))
        else:
            encodedPlayers.append(np.zeros((1,55)))
    encodedPots = []
    lastPot = np.zeros((1,9))
    for pot in game.pots:
        lastPot = encodePot(game, pot)
        encodedPots.append(lastPot)
    for i in range(8-len(encodedPots)):
        encodedPots.append(np.zeros((1,9)))
    encodedPots.append(lastPot)

    encodedTable = np.zeros((1,52))
    for card in game.table:
        encodedTable[0,card.suit*13+card.value]=1

    encodedPlayers=np.array(encodedPlayers)#440
    encodedPots = np.array(encodedPots)
    encodedPlayers = encodedPlayers.reshape((1,8*55))
    encodedPots = encodedPots.reshape((1,9*9))
    return np.concatenate((encodedPlayers, encodedPots, encodedTable, np.zeros((1,1))), axis=1)#8*55+9*9+52+1=574



def encodePlayer(player):
    result = np.zeros((1,55))
    result[0,player.card1.suit*13+player.card1.value]=1
    result[0,player.card2.suit*13+player.card2.value]=1
    result[0,52]=player.status
    result[0,53]=player.bet
    result[0,54]=player.money
    return result


def encodePot(game, pot):
    bets = np.zeros((1,9))
    for i in range(8):
        playerPos =  (i + game.turn)%8
        if playerPos < len(game.players):
            player = game.players[playerPos]
            bets[0,i] = pot.getPlayerBet(player)
    bets[0,8]=pot.size
    return bets