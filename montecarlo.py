'''
    Run Montecarlo simulation to calculate the probability of winning
    with a certain pokerhand given an amount of players
'''

import json
import operator
import numpy as np
from card_utils import CardUtils
from copy import copy
import time
from collections import Counter


class Montecarlo():

    CARD_RANKS = "23456789TJQKA"
    SUITS = 'CDHS'

    def __init__(self):
        self.cardUtils = CardUtils()

    # Creates a deck of cards

    def create_deck(self):
        ranks = self.CARD_RANKS
        suits = self.SUITS
        Deck = []
        # List comprehension to create combinations of values and suits
        [Deck.append(x + y) for x in ranks for y in suits]
        return Deck

    # Returns a list of pre flop equities ordered from lower to higher
    def get_preflop_equities(self):
        with open('./preflop-equity.json', 'r') as f:
            equities_dict = json.load(f)

        equities_sorted = sorted(
            equities_dict.items(), key=operator.itemgetter(1))

        return equities_sorted

    # Find the hand with the highest score
    def find_winning_hand(self, hands):
        scores = [(i, self.cardUtils.calculate_hand_score(hand))
                  for i, hand in enumerate(hands)]
        winner = sorted(scores, key=lambda x: x[1], reverse=True)[0][0]

        return hands[winner], scores[winner][1][-1]

    def get_opponent_allowed_cards(self, opponent_range):
        preflop_equity_list = self.get_preflop_equities()
        count = len(preflop_equity_list)
        take_top = int(count * opponent_range)
        allowed = set(list(preflop_equity_list)[-take_top:])
        allowed_cards = [i[0] for i in allowed]
        return set(allowed_cards)

    # Transform two cards to card short notation,
    # Example ["AH", "KH"] -> "AKs"
    def get_two_short_notation(self, input_cards, add_O_to_pairs=False):
        card1 = input_cards[0][0]
        card2 = input_cards[1][0]
        suited_str = 'S' if input_cards[0][1] == input_cards[1][1] else 'O'
        if card1[0] == card2[0]:
            if add_O_to_pairs:
                suited_str = "O"
            else:
                suited_str = ''

        return card1 + card2 + suited_str, card2 + card1 + suited_str

    def distribute_cards_to_players(self, deck, player_amount,
                                    player_card_list, known_table_cards,
                                    opponent_allowed_cards, passes):

        # Remove the known cards and put them in the table cards
        CardsOnTable = []
        for known_table_card in known_table_cards:
            CardsOnTable.append(deck.pop(deck.index(known_table_card)))

        all_players = []
        knownPlayers = 0

        for player_cards in player_card_list:
            known_player = []

            if type(player_cards) == set:
                while True:
                    passes + 1
                    random_card1 = np.random.randint(0, len(deck))
                    random_card2 = np.random.randint(0, len(deck) - 1)
                    if not random_card1 == random_card2:
                        crd1, crd2 = self.get_two_short_notation(
                            [deck[random_card1], deck[random_card2]])
                        if crd1 in player_cards and crd2 in player_cards:
                            break
                player_cards = []
                player_cards.append(deck[random_card1])
                player_cards.append(deck[random_card2])

            known_player.append(player_cards[0])
            known_player.append(player_cards[1])
            all_players.append(known_player)

            try:
                deck.pop(deck.index(player_cards[0]))
            except:
                pass
            try:
                deck.pop(deck.index(player_cards[1]))
            except:
                pass

            knownPlayers += 1

        for _ in range(player_amount - knownPlayers):
            random_player = []

            while True:
                passes += 1
                random_card1 = np.random.randint(0, len(deck))
                random_card2 = np.random.randint(0, len(deck) - 1)

                if not random_card1 == random_card2:
                    crd1, crd2 = self.get_two_short_notation([deck[random_card1],
                                                              deck[random_card2]])

                    if crd1 in opponent_allowed_cards or crd2 in opponent_allowed_cards:
                        break

            random_player.append(deck.pop(random_card1))
            random_player.append(deck.pop(random_card2))

            all_players.append(random_player)

        return all_players, deck, passes

    def distribute_cards_to_table(self, Deck, table_card_list):
        remaningRandoms = 5 - len(table_card_list)
        for n in range(0, remaningRandoms):
            table_card_list.append(
                Deck.pop(np.random.random_integers(0, len(Deck) - 1)))

        return table_card_list

    def run_montecarlo(self, original_player_list, original_table_card_list, player_amount, maxRuns, timeout, opponent_range=1):
        if type(opponent_range) == float or type(opponent_range) == int:
            opponent_allowed_cards = self.get_opponent_allowed_cards(
                opponent_range)
        elif type(opponent_range == set):
            opponent_allowed_cards = opponent_range

        winnerCardTypeList = []
        wins = 0
        runs = 0
        passes = 0
        OriginalDeck = self.create_deck()

        for m in range(maxRuns):
            runs += 1
            Deck = copy(OriginalDeck)
            PlayerCardList = copy(original_player_list)
            TableCardList = copy(original_table_card_list)
            Players, Deck, passes = self.distribute_cards_to_players(
                Deck, player_amount, PlayerCardList, TableCardList, opponent_allowed_cards, passes)

            Deck5Cards = self.distribute_cards_to_table(Deck, TableCardList)
            PlayerFinalCardsWithTableCards = []
            for o in range(0, player_amount):
                PlayerFinalCardsWithTableCards.append(Players[o] + Deck5Cards)

            bestHand, winnerCardType = self.find_winning_hand(
                PlayerFinalCardsWithTableCards)

            winner = (PlayerFinalCardsWithTableCards.index(bestHand))
            CollusionPlayers = 0
            if winner < CollusionPlayers + 1:
                wins += 1
                winnerCardTypeList.append(winnerCardType)
                # winnerlist.append(winner)
                # self.equity=wins/m
                # if self.equity>0.99: self.equity=0.99
                # EquityList.append(self.equity)

            if passes > 10000 and time.time() > timeout:
                break

        self.equity = np.round(float(wins)/(runs), 3)

        self.winnerCardTypeList = Counter(winnerCardTypeList)
        for key, value in self.winnerCardTypeList.items():
            self.winnerCardTypeList[key] = np.round(
                float(value) / float(runs), 3)

        self.winTypesDict = self.winnerCardTypeList.items()
        self.runs = runs
        self.passes = passes

        return self.equity, self.winTypesDict


mc = Montecarlo()

c = mc.run_montecarlo([["AS", "AD"]], [],
                      8, 12000, 12000, opponent_range=1)

print(c)
