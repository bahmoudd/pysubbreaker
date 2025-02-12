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
        
        # Calculate log probabilities
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

print("Substitution Cipher solver, you may have to wait several iterations")
print("for the correct result. Press Ctrl+C to exit program.")

# Function to apply deciphered text back into original format
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

# Keep going until we are killed by the user
i = 0
while True:
    i += 1
    random.shuffle(parentkey)
    deciphered = SimpleSub(parentkey).decipher("".join(letters_only))
    parentscore = fitness.score(deciphered)
    count = 0

    while count < 1000:
        a, b = random.sample(range(26), 2)
        child = parentkey[:]
        # Swap two characters in the child
        child[a], child[b] = child[b], child[a]
        deciphered = SimpleSub(child).decipher("".join(letters_only))
        score = fitness.score(deciphered)

        # If the child was better, replace the parent with it
        if score > parentscore:
            parentscore = score
            parentkey = child[:]
            count = 0
        count += 1

    # Keep track of best score seen so far
    if parentscore > maxscore:
        maxscore, maxkey = parentscore, parentkey[:]
        print(f"\nBest score so far: {maxscore} on iteration {i}")
        ss = SimpleSub(maxkey)
        decoded_text = ss.decipher(''.join(letters_only))
        formatted_output = restore_format(ctext, decoded_text)
        print(f'    Best key: {"".join(maxkey)}')
        print(f'    Plaintext: {formatted_output}')
