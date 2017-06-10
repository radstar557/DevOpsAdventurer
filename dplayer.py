#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#  dodPoker:  a poker server to run automated texas hold'em
#  poker rounds with bots
#  Copyright (C) 2017 wobe-systems GmbH
# -----------------------------------------------------------
# -----------------------------------------------------------
# Configuration
# You need to change the setting according to your environment
gregister_url='http://192.168.0.5:5001'
glocalip_adr='192.168.0.33'

# -----------------------------------------------------------

from flask import Flask, request
from flask_restful import Resource, Api
import sys

from requests import put
import json

app = Flask(__name__)
api = Api(app)

# Web API to be called from the poker manager
class PokerPlayerAPI(Resource):
    global poker
    def poker(hands):
        "Return the best hand: poker([hand,...]) => hand"
        return max(hands, key=hand_rank)

    global hand_rank
    def hand_rank(hand):
        ranks = card_ranks(hand)
        if straight(ranks) and flush(hand):  # straight flush
            return (8, max(ranks))
        elif kind(4, ranks):  # 4 of a kind
            return (7, kind(4, ranks), kind(1, ranks))
        elif kind(3, ranks) and kind(2, ranks):  # full house
            return (6, kind(3, ranks), kind(2, ranks))
        elif flush(hand):  # flush
            return (5, ranks)
        elif straight(ranks):  # straight
            return (4, max(ranks))
        elif kind(3, ranks):  # 3 of a kind
            return (3, kind(3, ranks), ranks)
        elif two_pair(ranks):  # 2 pair
            return (2, two_pair(ranks), ranks)
        elif kind(2, ranks):  # kind
            return (1, kind(2, ranks), ranks)
        else:  # high card
            return (0, ranks)

    global card_ranks
    def card_ranks(cards):
        "Return a list of the ranks,sorted with higher first"
        ranks = ['--23456789TJQKA'.index(r) for r, s in cards]
        ranks.sort(reverse=True)
        return ranks

    global straight
    def straight(ranks):
        "Return True if the ordered ranks from a 5-card straight"
        return (max(ranks) - min(ranks) == 4) and len(set(ranks)) == 5

    global flush
    def flush(hand):
        "Return True if all the cards have the same suit"
        suits = [s for r, s in hand]
        return len(set(suits)) == 1

    global kind
    def kind(n, ranks):
        for r in ranks:
            if ranks.count(r) == n: return r
        return None

    global two_pair
    def two_pair(ranks):
        pair = kind(2, ranks)
        lowpair = kind(2, list(reversed(ranks)))
        print(pair and lowpair)
        if pair and lowpair != pair:
            return (pair, lowpair)
        else:
            return None

    global test
    def test():
        "Test cases for the functions in poker program"
        sf = "6D 7C".split()  # Straight Flush
        fk = "9D 9H 9S 9C 7D".split()  # Four of a Kind
        fh = "TD TC TH 7C 7D".split()  # Full House
        # result of card_ranks(sf) is [10,9,8,7,6]
        # assert card_ranks(sf) == [10,9,8,7,6]
        # assert card_ranks(fk) == [9,9,9,9,7]
        # assert card_ranks(fh) == [10,10,10,7,7]
        # print(poker([sf]))
        print(hand_rank(fk))
        # poker([sf, fk, fh]) is sf
        # assert poker([sf, fk, fh]) == sf
        # assert poker([fk, fh]) == fk
        # assert poker([fh, fh]) == fh
        # assert poker([sf]) == sf
        # assert poker([sf] + 99*[fh]) == sf
        # assert hand_rank(sf) == (8, 10)
        # assert hand_rank(fk) == (7, 9, 7)
        # assert hand_rank(fh) == (6, 10, 7)
        return 'tests pass'

    ## return bid to caller
    #
    #  Depending on the cards passed to this function in the data parameter,
    #  this function has to return the next bid.
    #  The following rules are applied:
    #   -- fold --
    #   bid < min_bid
    #   bid > max_bid -> ** error **
    #   (bid > min_bid) and (bid < (min_bid+big_blind)) -> ** error **
    #
    #   -- check --
    #   (bid == 0) and (min_bid == 0) -> check
    #
    #   -- call --
    #   (bid == min_bid) and (min_bid > 0)
    #
    #   -- raise --
    #   min_bid + big_blind + x
    #   x is any value to increase on top of the Big blind
    #
    #   -- all in --
    #   bid == max_bid -> all in
    #
    #  @param data : a dictionary containing the following values - example: data['pot']
    #                min_bid   : minimum bid to return to stay in the game
    #                max_bid   : maximum possible bid
    #                big_blind : the current value of the big blind
    #                pot       : the total value of the current pot
    #                board     : a list of board cards on the table as string '<rank><suit>'
    #                hand      : a list of individual hand cards as string '<rank><suit>'
    #
    #                            <rank> : 23456789TJQKA
    #                            <suit> : 's' : spades
    #                                     'h' : hearts
    #                                     'd' : diamonds
    #                                     'c' : clubs
    #
    # @return a dictionary containing the following values
    #         bid  : a number between 0 and max_bid
    def __get_bid(self, data,bitAmount):
        # print('bit amount in gte_bid function ', bitAmount)
        return bitAmount

    # dispatch incoming get commands
    def get(self, command_id):

        data = request.form['data']
        data = json.loads(data)

        if command_id == 'get_bid':

            print(data)
            # print('Inside get')
            # print('min_bid:', data[u'min_bid'])
            # print('pot:', data[u'pot'])
            # print('big_blind:', data[u'big_blind'])
            # hand2 = print('hand[1]:', data[u'hand'][1]
            bitAmount = 0
            if data[u'hand'] :
                length = len(data[u'hand']) + len(data[u'board'])
                print("number of cards: ", length )
                #print(data[u'hand'] + data[u'board'])
                rank = hand_rank(data[u'hand'] + data[u'board'])
                print("rank : ", rank)
                if length == 2 :
                    print("in round 1")
                    #bitAmount = data[u'min_bid']
                    rankValue = rank[0]
                    if rankValue == 0:
                        bitAmount = data[u'min_bid'] + 0.20 * data[u'min_bid']
                    elif rankValue == 1:
                        bitAmount = data[u'min_bid'] + 0.20 * data[u'min_bid']
                    elif rankValue == 2:
                        bitAmount = data[u'min_bid'] + 0.25 * data[u'min_bid']
                    elif rankValue == 3:
                        bitAmount = data[u'min_bid'] + 0.25 * data[u'min_bid']
                    elif rankValue == 4:
                        bitAmount = data[u'min_bid'] + 0.30 * data[u'min_bid']
                    elif rankValue == 5:
                        bitAmount = data[u'min_bid'] + 0.40 * data[u'min_bid']
                    elif rankValue == 6:
                        bitAmount = data[u'min_bid'] + 0.50 * data[u'max_bid']
                    elif rankValue == 7:
                        bitAmount = data[u'min_bid'] + 0.60 * data[u'max_bid']
                    elif rankValue == 8:
                        bitAmount = data[u'min_bid'] + 0.70 * data[u'max_bid']
                    else:
                        bitAmount = data[u'min_bid']
                elif length == 5:
                    #print(rank[0])
                    print("in round 2")
                    rankValue = rank[0]
                    if rankValue == 0:
                        bitAmount = data[u'min_bid'] + 0.20 * data[u'max_bid']
                    elif rankValue == 1:
                        bitAmount = data[u'min_bid'] + 0.20 * data[u'max_bid']
                    elif rankValue == 2:
                        bitAmount = data[u'min_bid'] + 0.25 * data[u'max_bid']
                    elif rankValue == 3:
                        bitAmount = data[u'min_bid'] + 0.25 * data[u'max_bid']
                    elif rankValue == 4:
                        bitAmount = data[u'min_bid'] + 0.30 * data[u'max_bid']
                    elif rankValue == 5:
                        bitAmount = data[u'min_bid'] +  0.40 * data[u'max_bid']
                    elif rankValue == 6:
                        bitAmount = data[u'min_bid'] +  0.50 * data[u'max_bid']
                    elif rankValue == 7:
                        bitAmount = data[u'max_bid']
                    elif rankValue == 8:
                        bitAmount = data[u'max_bid']
                    else :
                        bitAmount = 0
                elif length == 6:
                    print("in round 3")
                    #print(rank[0])
                    rankValue = rank[0]
                    if rankValue == 0 :
                        bitAmount =  data[u'min_bid'] + 0.15 * data[u'max_bid']
                    elif rankValue == 1 :
                        bitAmount = data[u'min_bid'] + 0.15 * data[u'max_bid']
                    elif rankValue == 2:
                        bitAmount = data[u'min_bid'] + 0.15 * data[u'max_bid']
                    elif rankValue == 3:
                        bitAmount = data[u'min_bid'] + 0.20 * data[u'max_bid']
                    elif rankValue == 4:
                        bitAmount = data[u'min_bid'] + 0.30 * data[u'max_bid']
                    elif rankValue == 5:
                        bitAmount = data[u'min_bid'] +  0.40 * data[u'max_bid']
                    elif rankValue == 6:
                        bitAmount = data[u'min_bid'] +  0.50 * data[u'max_bid']
                    elif rankValue == 7:
                        bitAmount = data[u'max_bid']
                    elif rankValue == 8:
                        bitAmount = data[u'max_bid']
                    else :
                        bitAmount = 0
                elif length == 7:
                    print("in round 4")
                    # print(rank[0])
                    rankValue = rank[0]
                    if rankValue == 0:
                        bitAmount = data[u'min_bid'] + 0.15 * data[u'max_bid']
                    elif rankValue == 1:
                        bitAmount = data[u'min_bid'] + 0.15 * data[u'max_bid']
                    elif rankValue == 2:
                        bitAmount = data[u'min_bid'] + 0.15 * data[u'max_bid']
                    elif rankValue == 3:
                        bitAmount = data[u'min_bid'] + 0.20 * data[u'max_bid']
                    elif rankValue == 4:
                        bitAmount = data[u'min_bid'] + 0.30 * data[u'max_bid']
                    elif rankValue == 5:
                        bitAmount = data[u'min_bid'] +  0.40 * data[u'max_bid']
                    elif rankValue == 6:
                        bitAmount = data[u'min_bid'] +  0.50 * data[u'max_bid']
                    elif rankValue == 7:
                        bitAmount = data[u'max_bid']
                    elif rankValue == 8:
                        bitAmount = data[u'max_bid']
                    else:
                        bitAmount = 0
            if int(bitAmount) == 0 and data[u'min_bid'] == 0:
                print('In special case')
                bitAmount = 10

            if bitAmount > data[u'max_bid'] :
                bitAmount = data[u'max_bid']


            print('bit amount', int(bitAmount))

            return {'bid': self.__get_bid(data,int(bitAmount))}
        else:
            return {}, 201

    # dispatch incoming put commands (if any)
    def put(self, command_id):
        return 201


api.add_resource(PokerPlayerAPI, '/dpoker/player/v1/<string:command_id>')

# main function
def main():

    # run the player bot with parameters
    if len(sys.argv) == 4:
        team_name = sys.argv[1]
        api_port = int(sys.argv[2])
        api_url = 'http://%s:%s' % (glocalip_adr, api_port)
        api_pass = sys.argv[3]
    else:
        print("""
DevOps Poker Bot - usage instruction
------------------------------------
python3 dplayer.py <team name> <port> <password>
example:
    python dplayer Devops_Adventurer 40001 eraX1
        """)
        return 0


    # register player
    r = put("%s/dpoker/v1/enter_game"%gregister_url, data={'team': team_name, \
                                                           'url': api_url,\
                                                           'pass':api_pass}).json()
    if r != 201:
        raise Exception('registration failed: probably wrong team name')

    else:
        print('registration successful')
    try:
        app.run(host='0.0.0.0', port=api_port, debug=False)
    finally:
        put("%s/dpoker/v1/leave_game"%gregister_url, data={'team': team_name, \
                                                           'url': api_url,\
                                                           'pass': api_pass}).json()
# run the main function
if __name__ == '__main__':
    main()

