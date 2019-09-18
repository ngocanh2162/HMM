import re

class Prep(object): 
    def __init__(self, file_path, states):
        self.file_path = file_path
        self.states = states
        
    def getData(self):
        X = []
        f =  open(self.file_path, 'r', encoding="utf8")
        for line in f:
            x = ''.join(line.lower())
            x = x.replace("_", " ")
            x = x.replace(". ", ".. ")
            sentences = x.split(". ")
            for sen in sentences: 
                X.append(sen)
        return X

    def getSyllables(self, path):
        X = []
        f =  open(path, 'r', encoding="utf8") 
        for line in f:
            line = line.replace(",", "")
            line = line.replace(".", "")
            line = re.sub(r'[0-9]+', '', line.lower())
            temp =  line.lower().split()
            X += temp
        return X

    def str2words(self, text):
        X = []
        for line in text:
            x = ''.join(line)
            x = x.lower().split()
            X.append(x)
        return X

    def wordCount(self, X, syllables_path):
        word_count = {}
        hiddenStates = []
        syllables = self.getSyllables(syllables_path)
        for sentences in X:
            hiddenState = ''
            words = sentences.split()
            for word in words:
                if  word in word_count:
                    word_count[word] += 1
                else:
                    word_count[word] = 1
                if word not in syllables: #dau cau, so, tu nuoc ngoai, tu dung
                    hiddenState += 'O'
                else:
                    if len(hiddenState) > 0 and hiddenState[-1] == 'O':
                        hiddenState += 'B'
                    else:
                        hiddenState += ' '
            hiddenStates.append(hiddenState)
        return (hiddenStates, word_count)

    def BIOconf(self, X, word_count, test_wordcount, hidden_states):
        B = {}
        words = list(set(word_count.keys())|set(test_wordcount.keys()))
        M = len(self.states)
        for i in range(M):
            B[i] = {}
            for word in words:
                B[i][word] = 1.0/M
        for i in range(len(hidden_states)):
            length = len(hidden_states[i])
            for j in range(length):
                obser = X[i][j]
                hidden = hidden_states[i][j]
                if hidden == 'O': #B[observation=O] thì B[state=O]=1, B[state=B|I]=0
                    B[0][obser] = 0
                    B[1][obser] = 0
                    B[2][obser] = 1
        return B

    def convert(self, hidden_states): #convert the hidden_state string to list
        temp = []
        for index in range(len(hidden_states)):
            regex = re.compile("(\w{1})")
            states = [w for w in regex.split(hidden_states[index]) if w]
            if len(states) !=0:
                temp.append(states)
        return temp

    def word_sequence(self, test, o_hiddenstate):
        sequence = []
        for i in range(len(test)):
            length = len(test[i])
            temp = []
            j = 0
            while j < length:
                if o_hiddenstate[i][j] == 'O':
                    temp.append(test[i][j])
                else:
                    s = test[i][j]
                    j += 1
                    while o_hiddenstate[i][j] == 'B':
                        s += test[i][j]
                        k += 1 
                    s += test[i][j]
                    temp.append(s)
                k += 1
            sequence.append(' '.join(temp))
        return sequence