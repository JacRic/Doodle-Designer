# Jacob Richard COMP 4911 - Final Project
# This class holds a list of words that the players will draw in the game. 

import random

class WordPool:
    # List of words for the players can draw
    WORDS = [
    "A cup of coffee",
    "A cat chasing a butterfly",
    "A tree with a swing",
    "A smiling sun",
    "A book with glasses",
    "A flying bird",
    "A slice of pizza",
    "A happy face emoji",
    "A bicycle",
    "A snail with a shell",
    "A flower vase",
    "A cloud with raindrops",
    "A rocket ship",
    "A dancing stick figure",
    "A beach ball",
    "A house with a chimney",
    "A butterfly",
    "A hot air balloon",
    "A snowman",
    "A piece of cake"
]


    # Function to pick a random word from the list
    def pick_random_word(self):
        return random.choice(self.WORDS)
