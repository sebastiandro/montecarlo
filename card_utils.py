class CardUtils:

    CARD_RANKS = "23456789TJQKA"
    SUITS = 'CDHS'

    def get_score_and_rank(self, hand):

        # We create a dict with the index of the card rank, which in turn
        # gives the
        rcounts = {self.CARD_RANKS.find(r): ''.join(
            hand).count(r) for r, _ in hand}.items()

        # Create tuples of the number of instances of a card and the
        # card's rank. The cards are sorted by the occurences
        return zip(*sorted((cnt, rank)
                           for rank, cnt in rcounts)[::-1])

    def is_straight(self, card_ranks):
        sortedCrdRanks = sorted(card_ranks, reverse=True)
        straight = False

        for i in range(len(sortedCrdRanks) - 4):
            # If the difference between this rank and the 4 following
            # is 4, we know that is it a straight. Since we also know
            # that there's at least 5 unique cards.
            straight = sortedCrdRanks[i] - sortedCrdRanks[i+4] == 4

        return straight, i

    def calculate_hand_score(self, hand):
        score, card_ranks = self.get_score_and_rank(hand)

        potential_threeofakind = score[0] == 3
        potential_twopair = score == (2, 2, 1, 1, 1)
        potential_pair = score == (2, 1, 1, 1, 1, 1)

        # Full house, triples and a pair of a pair of triplets
        if score[0:2] == (3, 2) or score[0:2] == (3, 3):
            card_ranks = (card_ranks[0], card_ranks[1])
            score = (3, 2)
        # This is the case where we have three pairs, which in turns
        elif score[0:4] == (2, 2, 2, 1):
            score = (2, 2, 1)
            # The kicker is the the max rank of the lowest pair
            # and the last card
            kicker = max(card_ranks[2], card_ranks[3])
        # Four of a kind
        elif score[0] == 4:
            score = (4,)
            sortedCrdRanks = sorted(card_ranks, reverse=True)
            card_ranks = (sortedCrdRanks[0], sortedCrdRanks[1])

        # If our score is made up of more than 5 different cards
        elif len(score) >= 5:
            # then it could be a straight

            # If the ace is in our hand, we could have a 5 high straight
            if (12 in card_ranks):
                card_ranks += (-1,)

            # We sort the ranks from high to low
            sortedCrdRanks = sorted(card_ranks, reverse=True)
            straight, i = self.is_straight(card_ranks)

            if straight:
                card_ranks = tuple(sortedCrdRanks[i:i+5])

            # or it could be a flush
            suits = [s for _, s in hand]
            flush = max(suits.count(s) for s in suits) >= 5
            if flush:
                for flushSuit in self.SUITS:
                    if suits.count(flushSuit) >= 5:
                        break
                flushHand = [k for k in hand if flushSuit in k]

                score, card_ranks = self.get_score_and_rank(flushHand)

                # it could be a straight flush
                straight, _ = self.is_straight(card_ranks)

            # Now this is really slick. This tuple can be described as
            # If it is not a straight and not a flush, then we get no pair
            # If it is not a flush, but a straight we get flush etc.
            score = ([(1,), (3, 1, 2)], [(3, 1, 3), (5,)])[flush][straight]

        # Now if the higher hands did not match, we still have our pairs
        if score == (1,) and potential_threeofakind:
            score = (3, 1)
        if score == (1,) and potential_twopair:
            score = (2, 2, 1)
        if score == (1,) and potential_pair:
            score = (2, 1, 1)

        # Now lets classify the hand
        if score[0] == 5:
            hand_type = "StraightFlush"
        elif score[0] == 4:
            hand_type = "FourOfAKind"
        elif score[0:2] == (3, 2):
            hand_type = "FullHouse"
        elif score[0:3] == (3, 1, 3):
            hand_type = "Flush"
        elif score[0:3] == (3, 1, 2):
            hand_type = "Straight"
        elif score[0:2] == (3, 1):
            hand_type = "ThreeOfAKind"
        elif score[0:2] == (2, 2):
            hand_type = "TwoPair"
        elif score[0] == 2:
            hand_type = "Pair"
            card_ranks = card_ranks[:4]
        elif score[0] == 1:
            hand_type = "HighCard"
            card_ranks = card_ranks[:5]
        else:
            raise Exception("Card Type error!")

        return score, card_ranks, hand_type
