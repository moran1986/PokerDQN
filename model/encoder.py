# -*- coding: utf-8 -*-
import numpy as np

SIZE = 554

CARDS_SIZE = 0
MONEY_SIZE = 0


def getCurrentPlayerMoney(state):
    return state[0,6]-state[0,5]

def getCurrentPlayerPotBet(state):
    return state[0,7*8+8]-state[0,7*8]

def encodeGame(game):
    totalCards = []
    totalPlayerState = []
    for i in range(8):
        playerPos =  (i + game.turn)%8
        if playerPos < len(game.players):
            (playerCards, playerState) = encodePlayer(game.players[playerPos], game.players[game.turn], game.table)
            totalCards.append(playerCards)
            totalPlayerState.append(playerState)
        else:
            totalCards.append(np.zeros((1,52)))
            totalPlayerState.append(np.zeros((1,8)))

    encodedPots = []
    lastPot = np.zeros((1,9))
    for pot in game.pots:
        lastPot = encodePot(game, pot)
        encodedPots.append(lastPot)
    for i in range(8-len(encodedPots)):
        encodedPots.append(np.zeros((1,9)))
    encodedPots.insert(0,lastPot)

    encodedTable = np.zeros((1,52))
    for card in game.table:
        encodedTable[0,card.suit*13+card.value]=1
    totalCards.append(encodedTable)


    totalCards=np.array(totalCards)#472
    encodedPots = np.array(encodedPots)#81
    totalPlayerState = np.array(totalPlayerState)


    totalCards = totalCards.reshape((1,9*52))
    encodedPots = encodedPots.reshape((1,9*9))
    totalPlayerState = totalPlayerState.reshape((1,8*8))

    totalState = np.concatenate((totalPlayerState, encodedPots), axis=1)
    return (totalCards, totalState)


def encodePlayer(player, currentPlayer, table):
    playerCards = np.zeros((1,52))
    playerState = np.zeros((1,8))
    playerState[0,player.status]=1
    playerState[0,5]=player.bet
    playerState[0,6]=player.money
    playerState[0,7]=player.step
    #if player==currentPlayer:
    playerCards[0,player.card1.suit*13+player.card1.value]=1
    playerCards[0,player.card2.suit*13+player.card2.value]=1
    '''else:
        for suit in range(0,4):
            for value in range(0,13):
                result[0,7+suit*13+value]=45.0/52.0
        result[0,7+currentPlayer.card1.suit*13+currentPlayer.card1.value]=0
        result[0,7+currentPlayer.card2.suit*13+currentPlayer.card2.value]=0
        result[0,7+table[0].suit*13+table[0].value]=0
        result[0,7+table[1].suit*13+table[1].value]=0
        result[0,7+table[2].suit*13+table[2].value]=0
        result[0,7+table[3].suit*13+table[3].value]=0
        result[0,7+table[4].suit*13+table[4].value]=0'''
    #result[0,7+player.combination.priority]=1

    '''if 'value1' in player.combination.params:
        result[0,16]=player.combination.params['value1']
    if 'value2' in player.combination.params:
        result[0,17]=player.combination.params['value2']
    if 'value3' in player.combination.params:
        result[0,18]=player.combination.params['value3']
    if 'value4' in player.combination.params:
        result[0,19]=player.combination.params['value4']
    if 'value5' in player.combination.params:
        result[0,20]=player.combination.params['value5']'''
    return (playerCards, playerState)


def encodePot(game, pot):
    bets = np.zeros((1,9))
    for i in range(8):
        playerPos =  (i + game.turn)%8
        if playerPos < len(game.players):
            player = game.players[playerPos]
            bets[0,i] = pot.getPlayerBet(player)
    bets[0,8]=pot.size
    return bets