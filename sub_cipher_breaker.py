from pycipher import SimpleSubstitution as SimpleSub
import random
import re 
from math import log10

class NGramScore:
    def __init__(self, ngramfile, sep=' '):
        """ Load a file containing ngrams and counts, calculate log probabilities """
        self.ngrams = {}
        with open(ngramfile, 'r', encoding='utf-8') as f:
            for line in f:
                key, count = line.strip().split(sep)
                self.ngrams[key] = int(count)
        
        self.L = len(next(iter(self.ngrams)))
        self.N = sum(self.ngrams.values())

        # Calculate scores
        for key in self.ngrams:
            self.ngrams[key] = log10(self.ngrams[key] / self.N)
        
        self.floor = log10(0.01 / self.N)

    def score(self, text):
        """ Compute the score of text """
        score = 0
        for i in range(len(text) - self.L + 1):
            ngram = text[i:i + self.L]
            score += self.ngrams.get(ngram, self.floor)
        return score

fitness = NGramScore("quadgrams.txt")  # Load quadgram statistics

with open("input.txt") as file:
    ctext = file.read()

# Extract only the letters for processing
letters_only = re.findall(r"[A-Z]", ctext.upper())

maxkey = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
maxscore = float('-inf')
parentscore, parentkey = maxscore, maxkey[:]

print("Substitution Cipher solver, you may have to wait several iterations for the correct result.")
print("Press Ctrl+C to exit program.")

def restore_format(original, decoded):
    result = []
    idx = 0
    for char in original:
        if char.isalpha():
            if char.isupper():
                result.append(decoded[idx].upper())
            else:
                result.append(decoded[idx].lower())
            idx += 1
        else:
            result.append(char)
    return "".join(result)

import math

i = 0 
T = 10
cooling_rate = 0.00005 # Lower = slower cooling, more exploration. 

parentkey = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
random.shuffle(parentkey)
parentscore = fitness.score(SimpleSub(parentkey).decipher(''.join(letters_only)))

while T > 0.1:
    i += 1
    # Swap two random letters to create a new child key
    a, b = random.sample(range(26), 2)
    child = parentkey[:]
    child[a], child[b] = child[b], child[a]

    # Score the child key
    deciphered = SimpleSub(child).decipher("".join(letters_only))
    score = fitness.score(deciphered)

    # Accept if better or with some probability
    delta = score - parentscore
    if delta > 0 or math.exp(delta / T) > random.random():
        parentkey = child
        parentscore = score


        if score > maxscore:
            maxscore = score
            maxkey = child[:]
            decoded_text = SimpleSub(maxkey).decipher("".join(letters_only))
            formatted_output = restore_format(ctext, decoded_text)
            print(f"\nNew best score: {maxscore} at iteration {i}")
            print(f"    Key: {''.join(maxkey)}")
            print(f"    Text: {formatted_output}")

    
    T -= cooling_rate
