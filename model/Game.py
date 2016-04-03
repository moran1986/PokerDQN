# -*- coding: utf-8 -*-
import random
import numpy as np
import sys


class AllOtherFolded(Exception):
    def __init__(self, player):
        self.player=player

class Card:
    def __init__(self, suit, value):
        self.suit=suit
        self.value=value

    def __str__(self):
        return self.valueToStr()

    def suitToStr(self):
        if self.suit==0:
            return "пик"
        elif self.suit==1:
            return "треф"
        elif self.suit==2:
            return "бубей"
        elif self.suit==3:
            return "червей"
        raise Exception("Bad suit")

    def valueToStr(self):
        if self.value < 9:
            return str(self.value+2)
        elif self.value == 9:
            return "J"
        elif self.value == 10:
            return "Q"
        elif self.value == 11:
            return "K"
        elif self.value== 12:
            return "A"

class Combination:
    def __init__(self, priority, params):
        self.priority=priority
        #0 = HIGHER CARD
        #1 = PAIR
        #2 = TWO PAIRS
        #3 = SET
        #4 = STREET
        #5 = FLASH
        #6 = FULL HOUSE
        #7 = CARE
        #8 = STREET FLASH
        self.params=params

    def __cmp__(self, other):
        if self.priority != other.priority:
            return self.priority.__cmp__(other.priority)
        if self.priority==0:#HIGHER CARD
            return self.params['value'].__cmp__(other.params['value'])
        if self.priority==1:#PAIR
            return self.params['value'].__cmp__(other.params['value'])
        if self.priority==2:#TWO PAIRS
            res = self.params['value1'].__cmp__(other.params['value1'])
            if res!=0:
                return res
            return self.params['value2'].__cmp__(other.params['value2'])
        if self.priority==3:#SET
            return self.params['value'].__cmp__(other.params['value'])
        if self.priority==4:#STREET
            return self.params['value'].__cmp__(other.params['value'])
        if self.priority==5:#FLASH
            res = self.params['value1'].__cmp__(other.params['value1'])
            if res!=0:
                return res
            res = self.params['value2'].__cmp__(other.params['value2'])
            if res!=0:
                return res
            res = self.params['value3'].__cmp__(other.params['value3'])
            if res!=0:
                return res
            res = self.params['value4'].__cmp__(other.params['value4'])
            if res!=0:
                return res
            return self.params['value5'].__cmp__(other.params['value5'])
        if self.priority==6:#FULLHOUSE
            res = self.params['value1'].__cmp__(other.params['value1'])
            if res!=0:
                return res
            return self.params['value2'].__cmp__(other.params['value2'])
        if self.priority==7:#CARE
            return self.params['value'].__cmp__(other.params['value'])
        if self.priority==8:#STREET FLASH
            return self.params['value'].__cmp__(other.params['value'])



class Player:
    def __init__(self, title, initialMoney):
        self.title=title
        self.status=0
        #0 - PLAYING
        #1 - FOLD
        #2 - CALL/CHECK
        #3 - RAISE
        #4 - ALLIN
        self.bet=0
        self.money=initialMoney
        self.reward=0

    def giveHand(self, card1, card2):
        self.card1=card1
        self.card2=card2



def getPlayerKey(player):
    return player.combination

class Pot:
    def __init__(self):
        self.size=0
        self.playersMoney={}

    def bet(self, money, player):
        playerBetInPot = self.getPlayerBet(player)
        playerBetInPot += money
        self.playersMoney[player.title] = playerBetInPot
        if self.size < playerBetInPot:
            self.size = playerBetInPot

    def getPlayerBet(self, player):
        playerBetInPot = 0
        if player.title in self.playersMoney:
            playerBetInPot = self.playersMoney[player.title]
        return playerBetInPot


class Game:
    def __init__(self):
        self.players = []
        self.players.append(Player("P1", 100))
        self.players.append(Player("P2", 100))
        self.players.append(Player("P3", 100))
        self.players.append(Player("P4", 100))
        self.players.append(Player("P5", 100))
        self.players.append(Player("P6", 100))
        self.players.append(Player("P7", 100))
        self.players.append(Player("P8", 100))
        self.SB = 3
        self.BB = 5
        self.button=0
        self.turn = 0
        self.pots = []
        self.table = []
        self.globalDeck = []
        self.roundFinished=False
        for suit in range(4):
            for value in range(13):
                self.globalDeck.append(Card(suit, value))


    def startRound(self):
        self.roundFinished=False
        self.dealCards()
        self.makeInitialBets()
        self.turn = (self.button + 3)%len(self.players)

    def dealCards(self):
        self.deck = self.globalDeck[:]
        random.shuffle(self.deck)
        for player in self.players:
            player.giveHand(self.deck.pop(0), self.deck.pop(0))
        self.table = []
        for i in range(5):
            self.table.append(self.deck.pop(0))

    def makeInitialBets(self):
        for player in self.players:
            player.bet=0
            player.status=0

        sbPos = (self.button + 1)%len(self.players)
        sbPlayer = self.players[sbPos]
        sbPlayerBet = min(sbPlayer.money, self.SB)
        sbPlayer.bet+=sbPlayerBet

        bbPos = (self.button + 2)%len(self.players)
        bbPlayer = self.players[bbPos]
        bbPlayerBet = min(bbPlayer.money, self.BB)
        bbPlayer.bet+=bbPlayerBet

        self.pots = []
        firstPot = Pot()
        firstPot.bet(sbPlayerBet, sbPlayer)
        firstPot.bet(bbPlayerBet, bbPlayer)
        self.pots.append(firstPot)

    def doBet(self, money):
        currentPlayer = self.players[self.turn]
        currentPot = self.getCurrentPot()
        if money < currentPot.size - currentPot.getPlayerBet(currentPlayer) and money < currentPlayer.money-currentPlayer.bet:
            self.doFold()
        elif money < currentPot.size - currentPot.getPlayerBet(currentPlayer) and money == currentPlayer.money-currentPlayer.bet:
            self.doAllIn()
        elif money == currentPot.size - currentPot.getPlayerBet(currentPlayer):
            self.doCall()
        else:
            self.doRaise(money)

    def doFold(self):
        currentPlayer = self.players[self.turn]
        currentPlayer.status=1
        highlander = self.checkHighlander()
        if highlander is not None:
            self.updatePots()
            self.finishRound()
        elif self.checkNoOneNeedToRaise():
            self.updatePots()
            self.finishRound()
        else:
            self.moveToNextPlayer()

    def doCall(self):
        currentPlayer = self.players[self.turn]
        currentPot = self.getCurrentPot()
        bet = currentPot.size - currentPot.getPlayerBet(currentPlayer)
        currentPlayer.bet+=bet
        if currentPlayer.money == currentPlayer.bet:
            currentPlayer.status=4
        else:
            currentPlayer.status=2
        currentPot.bet(bet, currentPlayer)
        if self.checkNoOneNeedToRaise():
            self.updatePots()
            self.finishRound()
        else:
            self.moveToNextPlayer()

    def doRaise(self, money):
        currentPlayer = self.players[self.turn]
        currentPlayer.bet+=money
        if currentPlayer.bet == currentPlayer.money:
            currentPlayer.status=4
        else:
            currentPlayer.status=3
        currentPot = self.getCurrentPot()
        currentPot.bet(money, currentPlayer)
        self.moveToNextPlayer()

    #только когда размер банка больше денег у игрока
    def doAllIn(self):
        currentPlayer = self.players[self.turn]
        allInMoney = currentPlayer.money - currentPlayer.bet
        currentPot = self.getCurrentPot()
        currentPot.bet(allInMoney, currentPlayer)
        currentPlayer.status=4
        currentPlayer.bet += allInMoney
        if self.checkNoOneNeedToRaise():
            self.updatePots()
            self.finishRound()
        else:
            self.moveToNextPlayer()

    def updatePots(self):
        allInBets = set()
        currentPot = self.getCurrentPot()
        for player in self.players:
            if player.status==4 and player.title in currentPot.playersMoney:
                allInBets.add(currentPot.playersMoney[player.title])
        allInBets = list(allInBets)
        allInBets.sort()

        totalAllInBet = 0
        for allInBet in allInBets:
            totalAllInBet += allInBet
            if currentPot.size == totalAllInBet:
                break
            newPot = Pot()
            for playerTitle in currentPot.playersMoney:
                if currentPot.playersMoney[playerTitle] > totalAllInBet:
                    newPot.playersMoney[playerTitle] = currentPot.playersMoney[playerTitle] - totalAllInBet
            self.pots.append(newPot)
            currentPot=newPot

    def finishRound(self):
        winnerOrder = []
        for player in self.players:
            player.reward=0
            player.combination = self.calcCombination(player)
            if player.status!=1:
                winnerOrder.append(player)
        winnerOrder.sort(key=getPlayerKey)

        pots = self.pots[:]
        for winner in winnerOrder:
            notTakenPots = []
            for pot in pots:
                if winner.title in pot.playersMoney:
                    for playerTitle in pot.playersMoney:
                        winner.reward += pot.playersMoney[playerTitle]
                else:
                    notTakenPots.append(pot)
            pots = notTakenPots
        newPlayers = []
        for player in self.players:
            player.reward -= player.bet
            player.money += player.reward
            if player.money>0:
                newPlayers.append(player)
        self.players=newPlayers

        self.button = (self.button+1)%len(self.players)
        self.roundFinished=True

    def calcCombination(self, player):
        suits = [0]*4
        values = [0]*13
        cards = self.table[:]
        cards.append(player.card1)
        cards.append(player.card2)
        for card in cards:
            suits[card.suit] += 1
            values[card.value] += 1

        #0 = HIGHER CARD
        #1 = PAIR
        #2 = TWO PAIRS
        #3 = SET
        #4 = STREET
        #5 = FLASH
        #6 = FULL HOUSE
        #7 = CARE
        #8 = STREET FLASH
        params = {}
        priority = 0
        careValue = myindex(values, 4)
        setValue = myindex(values, 3)
        pairValue = myindex(values, 2)
        flash5 = myindex(suits, 5)
        flash6 = myindex(suits, 6)
        flash7 = myindex(suits, 7)
        flash = flash5!=-1 or flash6!=-1 or flash7!=-1
        street = self.getStreetPos(values)
        higherCard= self.getHigherCard(values)


        if careValue!=-1:
            priority = 7
            params['value']=careValue
        elif setValue!=-1 and pairValue!=-1:
            priority = 6
            params['value1']=setValue
            params['value2']=pairValue
        elif setValue!=-1:
            priority = 3
            params['value']=setValue
        elif pairValue!=-1:
            pairValue2 = myindex(values, 2, pairValue+1)
            if pairValue2!=-1:
                priority = 2
                params['value1']=pairValue2
                params['value2']=pairValue
            else:
                priority=1
                params['value']=pairValue
        elif flash and street!=-1:
            priority = 8
            params['value']=street
        elif street!=-1:
            priority = 4
            params['value']=street
        elif flash:
            priority=5
        else:
            priority=0
            params['value']=higherCard
        return Combination(priority, params)


    def getStreetPos(self, values):
        streetLength=0
        streetStart=-1
        for i in range(len(values)-1,0,-1):
            if values[i]!=0:
                if streetStart!=-1:
                    streetStart=i
                    streetLength=0
                streetLength+=1
                if streetLength==5:
                    return streetStart
            else:
                streetStart=-1
        return -1

    def getHigherCard(self, values):
        higher = 0
        for i in range(len(values)):
            if values[i]!=0:
                higher = i
        return i

    def moveToNextPlayer(self):
        current = self.turn
        self.turn = (self.turn + 1)%len(self.players)
        while self.players[self.turn].status==1 or self.players[self.turn].status==4:
            self.turn = (self.turn + 1)%len(self.players)

    def checkHighlander(self):
        highlander=None
        for player in self.players:
            if player.status!=1:
                if highlander is not None:
                    return None
                highlander=player
        return highlander

    def checkNoOneNeedToRaise(self):
        currentPot = self.getCurrentPot()
        for player in self.players:
            if player.status==1:
                continue
            if player.status==3 or player.status==0:
                return False
            if currentPot.getPlayerBet(player) < currentPot.size:
                return False
        return True

    def getCurrentPot(self):
        return self.pots[-1]


    def printGame(self):
        sys.stdout.write("\n\nTable: ")
        for card in self.table:
            sys.stdout.write(card.__str__()+" ")
        for player in self.players:
            sys.stdout.write("\n"+player.title+":")
            sys.stdout.write(player.card1.__str__()+" "+player.card2.__str__()+"; ")
            sys.stdout.write(str(player.money)+" // "+str(player.bet))
            if player.status == 1:
                sys.stdout.write(" FOLD")
            if player.status == 2:
                sys.stdout.write(" CHECK")
            if player.status == 3:
                sys.stdout.write(" RAISE")
            if player.status == 4:
                sys.stdout.write(" ALL-IN")


def myindex(ar, val, start=None):
    if start==None:
        start=len(ar)
    start=start-1
    for i in range(start,0,-1):
        if ar[i]==val:
            return i
    return -1
