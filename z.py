import re
syllables = "data/syllables.txt"

def getSyllables(path):
        X = []
        f =  open(path, 'r', encoding="utf8") 
        for line in f:
            line = line.replace(",", "")
            line = line.replace(".", "")
            line = re.sub(r'[0-9]+', '', line.lower())
            temp =  line.lower().split()
            X += temp
        return X

print(getSyllables(syllables))