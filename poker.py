# -*- coding: utf-8 -*-

suits = [':clubs:',':diamonds:',':heart:',':spades:']
numbers = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']


def poker(players):


    def roll(players):
        import random

        rolls = {}

        for player in players:
            rolls[player] = []

            while True:
                temp_roll = random.randint(1,52)
                if temp_roll not in rolls[player]:
                    rolls[player].append(temp_roll)
                    if len(rolls[player]) == 5:
                        break

        return rolls

    def convert(rolls):
        cards = {}

        for player in rolls:
            cards[player] = []

            for roll in rolls[player]:
                cards[player].append(numbers[roll % 13] + suits[roll // 13])

        return cards

    roll_sequence = roll(players)

    card_sequence = convert(roll_sequence)

    return card_sequence
