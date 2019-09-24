from HMM import Model
from pre import Prep
import re
import difflib

data = "data/train.txt"
syllables_path = "data/syllables.txt"
S = [0,1,2] #0:B, 1: I, 2: O
pro = Prep(data, S)
X, test = pro.getData()

hidden_states, word_count = pro.wordCount(X, syllables_path)
observation = word_count.keys()
X_train = pro.str2words(X)
observations_test = pro.str2words(test)
_, test_wordcount = pro.wordCount(test, syllables_path)

# fix cứng 
# A[state_from=O][state_to=B] =1, A[state_from=O][state_to=I|O] = 0
# B[observation = O] thì B[state=O]=1, B[state=B|I]=0
# phi(I) = 0

B = pro.BIOconf(X_train, word_count, test_wordcount, hidden_states)
phi = [0.9, 0, 0.1]
A = [[0.45, 0.35, 0.2], [0.6, 0.2, 0.2], [0.7, 0, 0.3]] 
model = Model(S, observation, phi, A, B)

phi, A, B = model.learningPhase(X_train, 3, A, B)

o_hiddenstate = []
for obser in pro.str2words(test):
    length = len(obser)
    i, sub_obser, state = 0, [], []
    y_state = model.decode(obser, word_count)
    o_hiddenstate.append(y_state)

word_sequence = pro.word_sequence(observations_test, o_hiddenstate)

def do_diff_both(a, b):
    delta, i = 0, 0
    while i < len(a) and i < len(b):
        delta += a[i] != b[i]
        i += 1
    delta += len(a[i:]) + len(b[i:])
    return delta
    
err = 0
for i in range(len(word_sequence)):
    err += do_diff_both(word_sequence[i], test[i])
err_t = test.count(' ')
print(err*100.0/err_t)
    
